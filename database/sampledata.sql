# Always use UTC timezone for all database
SET time_zone = '+0:00';

# Set the default settings
INSERT INTO settings(setting,value) VALUES('Simulation','YES');

# Create the default meters
INSERT INTO meters(description,unit,pin,bounce_time,pulse_value,pulse_factor) VALUES('Electricity','kWh',27,10,1,-3);
INSERT INTO meters(description,unit,pin,bounce_time,pulse_value,pulse_factor) VALUES('Gas','m3',17,10,1,-2);
