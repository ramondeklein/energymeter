import MySQLdb
from contextlib import closing
import time
import datetime
import logging

from config import configuration


# Setup logger
logger = logging.getLogger(__name__)

def get_sql_timestamp(t):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t))

def get_period(now, duration):
    gm_time = time.gmtime(now)
    seconds = (((gm_time.tm_hour * 60) + gm_time.tm_min) * 60) + gm_time.tm_sec
    start_seconds = int(seconds / duration) * duration
    return datetime.datetime(gm_time.tm_year, gm_time.tm_mon, gm_time.tm_mday, int(start_seconds / (60*60)), int(start_seconds / 60) % 60, start_seconds % 60)


class PulseLogging:
    def __init__(self, durations = [60, 15 * 60, 60 * 60]):
        # Initialize database
        self.db_instance = self.get_db(True)

        # Initialize durations
        self.durations = durations
        self.pulse_meters = {}

    def get_db(self, force_connect = False):
        if force_connect or not self.db_instance:
            # Determine the current configuration
            hostname = configuration.get('database', 'hostname') if configuration.has_option('database', 'hostname') else 'localhost'
            port = configuration.getint('database', 'port') if configuration.has_option('database', 'port') else 2206
            username = configuration.get('database', 'username') if configuration.has_option('database', 'username') else 'root'
            password = configuration.get('database', 'password') if configuration.has_option('database', 'password') else ''
            database = configuration.get('database', 'database') if configuration.has_option('database', 'database') else 'energymeter'

            try:
                # Connect to the database
                self.db_instance = MySQLdb.connect(host=hostname, port=port, user=username, passwd=password, db=database)

                # Always use UTC
                self.db_instance.cursor().execute("SET time_zone = '+0:00'")
            except Exception as exc:
                logger.error('Unable to establish database connection: %s' % (exc.message))
                raise

        return self.db_instance

    def log_pulse(self, meter, increment = 1):
        # Save the current timestamp
        now = time.time()

        # Check if the meter exists
        pulse_meter = self.pulse_meters.get(meter.id)
        if not pulse_meter:
            # Create a new meter object
            pulse_meter = self.pulse_meters[meter.id] = {
                'meter': meter,
                'last_pulse': 0
            }
            for duration in self.durations:
                pulse_meter[duration] = {
                    'last_period': None,
                    'complete': False
                }

        # Now can be before lastPulse if the clock is adjusted
        last_pulse = pulse_meter['last_pulse']
        if last_pulse:
            delta = int((now - last_pulse)*1000) if now > last_pulse else 0
        else:
            delta = 0
        pulse_meter['last_pulse'] = now

        # Save the pulse into the database
        try:
            db = self.get_db()
            with closing(db.cursor()) as cur:
                # Calculate the actual power
                actual_power = 0

                # Insert pulse record
                cur.execute("INSERT INTO pulse_readings(meter_ref,timestamp,milli_sec,delta) VALUES(%s,%s,%s,%s)", (meter.id, get_sql_timestamp(now), int(round(now * 1000)) % 1000, delta))
                if delta > 0:
                    logger.debug('%s: Pulse written (delta=%d.%03ds, actual=%d%s)' % (meter.description, int(delta / 1000), int(delta % 1000), int(round((3600.0 / delta) * meter.current_factor)), meter.current_unit))
                else:
                    logger.debug('%s: Initial pulse written' % (meter.description))

                # Save all durations
                for duration in self.durations:
                    meter_duration = pulse_meter[duration]
                    last_period = meter_duration['last_period']
                    current_period = get_period(now, duration)
                    if last_period and (last_period == current_period):
                        # Increment the number of pulses
                        meter_duration['pulses'] = meter_duration['pulses']+increment
                    else:
                        # If we had a previous period, then it's complete now and we can save it. We don't
                        # save the invalid periods, because they contain incomplete data.
                        if last_period:
                            pulses = meter_duration['pulses']
                            if meter_duration['complete']:
                                cur.execute("INSERT INTO pulse_readings_per_duration(meter_ref,duration,timestamp,pulses) VALUES(%s,%s,%s,%s)", (meter.id, duration, last_period, pulses));
                                logger.debug("{}: Pulse duration written ({} [{}s], {} pulses)".format(meter.description, last_period, duration, pulses))
                            else:
                                logger.debug("{}: Incomplete duration record is not written ({} [{}s], {} pulses)".format(meter.description, last_period, duration, pulses))
                            meter_duration['complete'] = True

                        # Initialize the new period
                        meter_duration['last_period'] = current_period
                        meter_duration['pulses'] = increment

                # Commit changes
                db.commit()

        except Exception as exc:
            # Log error
            logger.error("Unable to log pulse to the database: %s." % (exc.message))
            logger.error("Rendering current durations invalid for this meter")

            # Reset database
            self.db_instance = None

            # Reset complete status for the period
            for duration in self.durations:
                pulse_meter[duration]['complete'] = False
