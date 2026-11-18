USE ride_hailing;
CREATE ROLE 'ride_hailing_app';
GRANT SELECT ON ride_hailing.* TO 'ride_hailing_app';
GRANT INSERT ON ride_hailing.app_user TO 'ride_hailing_app';
GRANT INSERT ON ride_hailing.passenger TO 'ride_hailing_app';
GRANT INSERT ON ride_hailing.driver TO 'ride_hailing_app';
GRANT INSERT ON ride_hailing.vehicle TO 'ride_hailing_app';
GRANT INSERT ON ride_hailing.insurance_policy TO 'ride_hailing_app';
GRANT INSERT ON ride_hailing.driver_shift TO 'ride_hailing_app';
GRANT INSERT (trip_id,passenger_id,requested_at,origin_zone,destination_zone,service_type,estimated_km,estimated_fare)
 ON ride_hailing.trip TO 'ride_hailing_app';
GRANT INSERT,UPDATE ON ride_hailing.review TO 'ride_hailing_app';
GRANT EXECUTE ON PROCEDURE ride_hailing.assign_trip TO 'ride_hailing_app';
GRANT EXECUTE ON PROCEDURE ride_hailing.start_trip TO 'ride_hailing_app';
GRANT EXECUTE ON PROCEDURE ride_hailing.complete_trip TO 'ride_hailing_app';
GRANT EXECUTE ON PROCEDURE ride_hailing.cancel_trip TO 'ride_hailing_app';
-- Provision actual application accounts separately. Never grant the app owner privileges.
