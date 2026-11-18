from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=[]
p.append('USE ride_hailing;\nDELIMITER $$')
p.append('''CREATE TRIGGER vehicle_owner_fixed BEFORE UPDATE ON vehicle FOR EACH ROW
BEGIN
 IF NEW.driver_id<>OLD.driver_id THEN
 SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Vehicle ownership is fixed in this observation period';
 END IF;
END$$''')
p.append('''CREATE TRIGGER completed_guard BEFORE INSERT ON completed_trip FOR EACH ROW
BEGIN
 IF NOT EXISTS(SELECT 1 FROM trip WHERE trip_id=NEW.trip_id AND status='IN_PROGRESS'
 AND started_at<=NEW.ended_at) OR EXISTS(SELECT 1 FROM cancelled_trip WHERE trip_id=NEW.trip_id) THEN
 SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Completion requires an active trip and valid end time';
 END IF;
END$$''')
p.append('''CREATE TRIGGER cancelled_guard BEFORE INSERT ON cancelled_trip FOR EACH ROW
BEGIN
 IF NOT EXISTS(SELECT 1 FROM trip WHERE trip_id=NEW.trip_id AND status IN ('REQUESTED','ASSIGNED')
 AND requested_at<=NEW.cancelled_at) OR EXISTS(SELECT 1 FROM completed_trip WHERE trip_id=NEW.trip_id) THEN
 SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Cancellation requires an unstarted trip and valid time';
 END IF;
END$$''')
# Procedures are transaction boundaries. Invoke from a connection without a surrounding transaction.
def proc(name,args,decl,body):
 p.append(f'''CREATE PROCEDURE {name}({args}) SQL SECURITY DEFINER
BEGIN
 DECLARE v_status VARCHAR(12) DEFAULT NULL;
 {decl}
 DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
 START TRANSACTION;
 {body}
 COMMIT;
END$$''')
lock="SELECT status INTO v_status FROM trip WHERE trip_id=p_trip FOR UPDATE;"
proc('assign_trip','IN p_trip INT, IN p_driver INT, IN p_plate VARCHAR(12)','',f'''{lock}
 IF v_status IS NULL OR v_status<>'REQUESTED' THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Expected REQUESTED'; END IF;
 IF NOT EXISTS(SELECT 1 FROM vehicle WHERE plate=p_plate AND driver_id=p_driver) THEN
 SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Driver and vehicle mismatch'; END IF;
 UPDATE trip SET plate=p_plate,status='ASSIGNED' WHERE trip_id=p_trip;''')
proc('start_trip','IN p_trip INT, IN p_start DATETIME','',f'''{lock}
 IF v_status IS NULL OR v_status<>'ASSIGNED' THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Expected ASSIGNED'; END IF;
 UPDATE trip SET status='IN_PROGRESS',started_at=p_start WHERE trip_id=p_trip;''')
proc('complete_trip','IN p_trip INT, IN p_end DATETIME, IN p_base DECIMAL(10,2), IN p_tip DECIMAL(10,2), IN p_km DECIMAL(8,2), IN p_extra DECIMAL(10,2)','',f'''{lock}
 IF v_status IS NULL OR v_status<>'IN_PROGRESS' THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Expected IN_PROGRESS'; END IF;
 INSERT INTO completed_trip VALUES(p_trip,p_end,p_base,p_tip,p_km);
 -- Validate after inserting the detail to demonstrate rollback of a partial operation.
 IF p_extra IS NULL OR p_extra<0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Invalid surcharge'; END IF;
 IF p_extra>0 THEN INSERT INTO surcharge VALUES(p_trip,p_extra); END IF;
 UPDATE trip SET status='COMPLETED' WHERE trip_id=p_trip;''')
proc('cancel_trip','IN p_trip INT, IN p_cancel DATETIME, IN p_reason VARCHAR(160)','',f'''{lock}
 IF v_status IS NULL OR v_status NOT IN ('REQUESTED','ASSIGNED') THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Expected unstarted trip'; END IF;
 INSERT INTO cancelled_trip VALUES(p_trip,p_cancel,p_reason);
 UPDATE trip SET status='CANCELLED' WHERE trip_id=p_trip;''')
p.append('DELIMITER ;')
p.append('''CREATE VIEW trip_service AS
SELECT t.*,v.driver_id FROM trip t LEFT JOIN vehicle v ON v.plate=t.plate;
CREATE VIEW trip_financials AS
SELECT t.trip_id,t.passenger_id,t.plate,v.driver_id,t.requested_at,c.ended_at,
 t.estimated_fare,c.base_fare,c.tip,COALESCE(s.amount,0) AS surcharge,
 c.base_fare+c.tip+COALESCE(s.amount,0) AS total_fare,c.actual_km
FROM trip t JOIN completed_trip c ON c.trip_id=t.trip_id
JOIN vehicle v ON v.plate=t.plate LEFT JOIN surcharge s ON s.trip_id=t.trip_id;''')
(root/'sql/02_logic.sql').write_text('\n\n'.join(p))
