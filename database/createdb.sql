# We need to use the MYISAM engine to ensure proper performance on the Raspberry Pi

# Always use UTC timezone for all database
SET time_zone = '+0:00';

# Drop the old database
DROP DATABASE IF EXISTS energymeter;

# Create the database if it doesn't exist
CREATE DATABASE energymeter;
USE energymeter;

# Create the versions table
CREATE TABLE IF NOT EXISTS `versions` (
  `version`   SMALLINT       NOT NULL,
  `timestamp` TIMESTAMP      NOT NULL
) ENGINE = MYISAM;
INSERT `versions`(`version`,`timestamp`) VALUES(1,NOW());

# Create the pulse_readings table (contains a record for each pulse)
CREATE TABLE `pulse_readings` (
  `meter_ref`   SMALLINT     NOT NULL,
  `timestamp`   TIMESTAMP    NOT NULL,
  `milli_sec`   SMALLINT     NOT NULL,    -- Required, because older MySQL version don't support TIMESTAMP(3)
  `delta`       INT          NOT NULL,

  PRIMARY KEY (`meter_ref`, `timestamp`, `milli_sec`)
) ENGINE = MYISAM;

# Create the pulse_readings_per_duration table (contains the number of pulses per duration)
CREATE TABLE `pulse_readings_per_duration` (
  `meter_ref`    SMALLINT    NOT NULL,
  `duration`     SMALLINT    NOT NULL,
  `timestamp`    TIMESTAMP   NOT NULL,
  `usage`        FLOAT       NOT NULL,
  `min_power`    FLOAT       NOT NULL,
  `max_power`    FLOAT       NOT NULL,

  PRIMARY KEY (`meter_ref`, `duration`, `timestamp`)
) ENGINE = MYISAM;

# Create new user
CREATE USER 'emuser'@'%' IDENTIFIED BY 'em2015';
GRANT ALL PRIVILEGES ON energymeter.* TO 'emuser'@'%' WITH GRANT OPTION;
