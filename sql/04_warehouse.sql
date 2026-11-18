USE ride_hailing;
-- Independent analytical snapshot: four tables in addition to the 11 OLTP tables.
CREATE TABLE dw_date (date_key DATE PRIMARY KEY, calendar_year SMALLINT NOT NULL,
 calendar_month SMALLINT NOT NULL, day_of_month SMALLINT NOT NULL);
CREATE TABLE dw_driver (driver_key INT PRIMARY KEY, driver_name VARCHAR(80) NOT NULL);
CREATE TABLE dw_vehicle (vehicle_key VARCHAR(12) PRIMARY KEY, model VARCHAR(40) NOT NULL,
 capacity SMALLINT NOT NULL);
CREATE TABLE dw_trip_fact (
 trip_id INT PRIMARY KEY, date_key DATE NOT NULL, driver_key INT NOT NULL,
 vehicle_key VARCHAR(12) NOT NULL, total_fare DECIMAL(10,2) NOT NULL,
 actual_km DECIMAL(8,2) NOT NULL, estimated_fare DECIMAL(10,2) NOT NULL,
 FOREIGN KEY(date_key) REFERENCES dw_date(date_key),
 FOREIGN KEY(driver_key) REFERENCES dw_driver(driver_key),
 FOREIGN KEY(vehicle_key) REFERENCES dw_vehicle(vehicle_key));
INSERT INTO dw_date SELECT DISTINCT DATE(ended_at),YEAR(ended_at),MONTH(ended_at),DAY(ended_at) FROM trip_financials;
INSERT INTO dw_driver SELECT d.driver_id,u.full_name FROM driver d JOIN app_user u ON u.user_id=d.driver_id;
INSERT INTO dw_vehicle SELECT plate,model,capacity FROM vehicle;
INSERT INTO dw_trip_fact SELECT trip_id,DATE(ended_at),driver_id,plate,total_fare,actual_km,estimated_fare FROM trip_financials;
