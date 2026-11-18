USE ride_hailing;

-- version
SELECT VERSION() AS version;

-- counts
SELECT 'app_user' AS table_name,COUNT(*) AS rows_n FROM app_user UNION ALL SELECT 'passenger',COUNT(*) FROM passenger UNION ALL SELECT 'driver',COUNT(*) FROM driver UNION ALL SELECT 'vehicle',COUNT(*) FROM vehicle UNION ALL SELECT 'insurance_policy',COUNT(*) FROM insurance_policy UNION ALL SELECT 'driver_shift',COUNT(*) FROM driver_shift UNION ALL SELECT 'trip',COUNT(*) FROM trip UNION ALL SELECT 'completed_trip',COUNT(*) FROM completed_trip UNION ALL SELECT 'cancelled_trip',COUNT(*) FROM cancelled_trip UNION ALL SELECT 'review',COUNT(*) FROM review UNION ALL SELECT 'surcharge',COUNT(*) FROM surcharge;

-- status
SELECT status,COUNT(*) AS trips,ROUND(100*COUNT(*)/(SELECT COUNT(*) FROM trip),2) AS percent_all FROM trip GROUP BY status ORDER BY status;

-- finance
SELECT COUNT(*) AS completed,SUM(total_fare) AS total_fare,ROUND(AVG(total_fare),2) AS mean_fare,ROUND(AVG(total_fare-estimated_fare),2) AS mean_difference,SUM(surcharge) AS surcharges,SUM(tip) AS tips FROM trip_financials;

-- drivers
SELECT d.driver_id,COUNT(f.trip_id) AS completed,COALESCE(SUM(f.total_fare),0) AS gross_fare,ROUND(AVG(r.passenger_score),2) AS mean_score,COUNT(r.passenger_score) AS scored FROM driver d LEFT JOIN trip_financials f ON f.driver_id=d.driver_id LEFT JOIN review r ON r.trip_id=f.trip_id GROUP BY d.driver_id ORDER BY gross_fare DESC;

-- insurance
SELECT policy_id,plate,valid_to FROM insurance_policy WHERE valid_to BETWEEN '2026-11-01' AND DATE_ADD('2026-11-01',INTERVAL 30 DAY) ORDER BY policy_id;

-- daily
SELECT date_key,COUNT(*) AS trips,SUM(total_fare) AS gross_fare FROM dw_trip_fact GROUP BY date_key ORDER BY date_key;

-- rollup
SELECT d.calendar_year,d.calendar_month,v.model,COUNT(*) AS trips,SUM(f.total_fare) AS gross_fare FROM dw_trip_fact f JOIN dw_date d ON d.date_key=f.date_key JOIN dw_vehicle v ON v.vehicle_key=f.vehicle_key GROUP BY d.calendar_year,d.calendar_month,v.model WITH ROLLUP;

-- window
SELECT date_key,SUM(total_fare) AS daily_fare,LAG(SUM(total_fare)) OVER(ORDER BY date_key) AS previous_day_fare FROM dw_trip_fact GROUP BY date_key ORDER BY date_key;

-- nested
SELECT driver_id,ROUND(AVG(total_fare),2) AS mean_fare FROM trip_financials GROUP BY driver_id HAVING AVG(total_fare)>(SELECT AVG(total_fare) FROM trip_financials);

-- explain
EXPLAIN SELECT trip_id,status FROM trip WHERE passenger_id=101 AND requested_at>='2026-10-05' AND requested_at<'2026-10-10';