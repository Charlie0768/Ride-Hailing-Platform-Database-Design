-- MySQL 8.4. Dedicated schema; never drops an existing database.
CREATE DATABASE ride_hailing CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE ride_hailing;
CREATE TABLE app_user (
 user_id INT PRIMARY KEY, full_name VARCHAR(80) NOT NULL,
 phone VARCHAR(20) NOT NULL UNIQUE, email VARCHAR(120), birth_date DATE
) ENGINE=InnoDB;
CREATE TABLE passenger (
 passenger_id INT PRIMARY KEY, tier VARCHAR(10) NOT NULL DEFAULT 'STANDARD',
 FOREIGN KEY(passenger_id) REFERENCES app_user(user_id),
 CHECK(tier IN ('STANDARD','GOLD','PLATINUM'))
) ENGINE=InnoDB;
CREATE TABLE driver (
 driver_id INT PRIMARY KEY, license_no VARCHAR(30) NOT NULL UNIQUE,
 lifetime_km DECIMAL(12,2) NOT NULL DEFAULT 0,
 FOREIGN KEY(driver_id) REFERENCES app_user(user_id), CHECK(lifetime_km>=0)
) ENGINE=InnoDB;
CREATE TABLE vehicle (
 plate VARCHAR(12) PRIMARY KEY, driver_id INT NOT NULL,
 model VARCHAR(40) NOT NULL, color VARCHAR(20) NOT NULL,
 capacity SMALLINT NOT NULL,
 FOREIGN KEY(driver_id) REFERENCES driver(driver_id), CHECK(capacity BETWEEN 2 AND 9)
) ENGINE=InnoDB;
CREATE TABLE insurance_policy (
 policy_id INT PRIMARY KEY, plate VARCHAR(12) NOT NULL,
 valid_from DATE NOT NULL, valid_to DATE NOT NULL,
 FOREIGN KEY(plate) REFERENCES vehicle(plate), CHECK(valid_to>=valid_from)
) ENGINE=InnoDB;
CREATE TABLE driver_shift (
 driver_id INT NOT NULL, shift_start DATETIME NOT NULL, shift_end DATETIME,
 PRIMARY KEY(driver_id,shift_start), FOREIGN KEY(driver_id) REFERENCES driver(driver_id),
 CHECK(shift_end IS NULL OR shift_end>shift_start)
) ENGINE=InnoDB;
CREATE TABLE trip (
 trip_id INT PRIMARY KEY, passenger_id INT NOT NULL, plate VARCHAR(12),
 requested_at DATETIME NOT NULL, started_at DATETIME,
 origin_zone VARCHAR(30) NOT NULL, destination_zone VARCHAR(30) NOT NULL,
 service_type VARCHAR(12) NOT NULL, estimated_km DECIMAL(8,2) NOT NULL,
 estimated_fare DECIMAL(10,2) NOT NULL, status VARCHAR(12) NOT NULL DEFAULT 'REQUESTED',
 FOREIGN KEY(passenger_id) REFERENCES passenger(passenger_id),
 FOREIGN KEY(plate) REFERENCES vehicle(plate),
 CHECK(service_type IN ('STANDARD','COMFORT')),
 CHECK(estimated_km>0 AND estimated_fare>=0),
 CHECK(status IN ('REQUESTED','ASSIGNED','IN_PROGRESS','COMPLETED','CANCELLED')),
 CHECK(started_at IS NULL OR started_at>=requested_at),
 CHECK((status='REQUESTED' AND plate IS NULL AND started_at IS NULL)
 OR (status='ASSIGNED' AND plate IS NOT NULL AND started_at IS NULL)
 OR (status IN ('IN_PROGRESS','COMPLETED') AND plate IS NOT NULL AND started_at IS NOT NULL)
 OR (status='CANCELLED' AND started_at IS NULL)),
 INDEX ix_trip_passenger_time(passenger_id,requested_at),
 INDEX ix_trip_status_time(status,requested_at)
) ENGINE=InnoDB;
CREATE TABLE completed_trip (
 trip_id INT PRIMARY KEY, ended_at DATETIME NOT NULL,
 base_fare DECIMAL(10,2) NOT NULL, tip DECIMAL(10,2) NOT NULL DEFAULT 0,
 actual_km DECIMAL(8,2) NOT NULL,
 FOREIGN KEY(trip_id) REFERENCES trip(trip_id),
 CHECK(base_fare>=0 AND tip>=0 AND actual_km>0)
) ENGINE=InnoDB;
CREATE TABLE cancelled_trip (
 trip_id INT PRIMARY KEY, cancelled_at DATETIME NOT NULL,
 reason VARCHAR(160) NOT NULL,
 FOREIGN KEY(trip_id) REFERENCES trip(trip_id)
) ENGINE=InnoDB;
CREATE TABLE review (
 trip_id INT PRIMARY KEY, passenger_score SMALLINT, passenger_comment VARCHAR(200),
 driver_score SMALLINT, driver_comment VARCHAR(200),
 FOREIGN KEY(trip_id) REFERENCES completed_trip(trip_id),
 CHECK(passenger_score BETWEEN 0 AND 100), CHECK(driver_score BETWEEN 0 AND 100),
 CHECK(passenger_score IS NOT NULL OR driver_score IS NOT NULL)
) ENGINE=InnoDB;
CREATE TABLE surcharge (
 trip_id INT PRIMARY KEY, amount DECIMAL(10,2) NOT NULL,
 FOREIGN KEY(trip_id) REFERENCES completed_trip(trip_id), CHECK(amount>0)
) ENGINE=InnoDB;
