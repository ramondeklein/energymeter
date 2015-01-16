# Always use UTC timezone for all database
SET time_zone = '+0:00';

# Set the default settings
INSERT INTO settings(setting,value) VALUES('metering:live_mode','YES');

# Create the default meters
INSERT INTO meters(description,unit,pin,bounce_time,input_type,event_type,pulse_value,pulse_factor) VALUES('Electricity','kWh',22,10,2,2,1,-3);
INSERT INTO meters(description,unit,pin,bounce_time,input_type,event_type,pulse_value,pulse_factor) VALUES('Gas','m3',27,10,2,2,1,-2);
