# We need to use the MYISAM engine to ensure proper performance on the Raspberry Pi

# Always use UTC timezone for all database
SET time_zone = '+0:00';

DROP DATABASE metering;

# Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS metering;
USE metering;

# Create the versions table
CREATE TABLE IF NOT EXISTS versions (
  version   INT       NOT NULL,
  timestamp TIMESTAMP NOT NULL
);
INSERT versions(version,timestamp) VALUES(1,NOW());

CREATE TABLE settings (
  setting      VARCHAR(25) NOT NULL,
  value        VARCHAR(100),
  PRIMARY KEY (setting)
) ENGINE = MYISAM;

# Create the meter definition table
CREATE TABLE meters (
  id           SMALLINT     NOT NULL AUTO_INCREMENT,
  description  VARCHAR(100) NOT NULL,
  unit         VARCHAR(20)  NOT NULL,
  pin          TINYINT      NOT NULL,
  bounce_time  SMALLINT     NOT NULL DEFAULT 10,	
  pulse_value  SMALLINT     NOT NULL DEFAULT 1,
  pulse_factor SMALLINT     NOT NULL DEFAULT 0,
  PRIMARY KEY (id)
) ENGINE = MYISAM;

ALTER TABLE meters ADD CONSTRAINT ux_meters_description UNIQUE (description);
ALTER TABLE meters ADD CONSTRAINT ux_meters_pin UNIQUE (pin);

CREATE TABLE pulse_readings (
  meter_ref   SMALLINT     NOT NULL,
  timestamp   TIMESTAMP(3) NOT NULL,
  delta       MEDIUMINT    NULL
) ENGINE = MYISAM;

ALTER TABLE pulse_readings ADD CONSTRAINT FOREIGN KEY fk_pulse_readings_meter(meter_ref) REFERENCES meters(id) ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE pulse_readings_per_duration (
  meter_ref    SMALLINT    NOT NULL,
  duration     SMALLINT    NOT NULL,
  timestamp    TIMESTAMP   NOT NULL,
  pulses       SMALLINT    NOT NULL DEFAULT 0,
    
  PRIMARY KEY (meter_ref, duration, timestamp)
) ENGINE = MYISAM;

ALTER TABLE pulse_readings_per_duration ADD CONSTRAINT FOREIGN KEY fk_pulse_readings_per_duration_meter(meter_ref) REFERENCES meters(id) ON DELETE CASCADE ON UPDATE CASCADE;
