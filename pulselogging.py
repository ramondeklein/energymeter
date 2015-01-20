import logging
import MySQLdb
import time
from contextlib import closing


# Setup logger
logger = logging.getLogger(__name__)


def get_sql_timestamp(t):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t))


def get_start_period(t, duration):
    # Determine the seconds in the current day
    gm_time = time.gmtime(t)
    seconds_in_day = int((((gm_time.tm_hour * 60) + gm_time.tm_min) * 60) + gm_time.tm_sec)

    # Store the date part (number of seconds from epoch)
    date_offset = int(t - seconds_in_day)
    period_index = int(seconds_in_day / duration)

    # Determine the current period
    return float(date_offset + (period_index * duration))


def get_cost_time(t):
    local_time = time.localtime(t)
    return (local_time.tm_hour * 60) + local_time.tm_min


class PulseDurations:
    def __init__(self, pulse_meter, duration):
        self.pulse_meter = pulse_meter
        self.duration = duration
        self.period = None
        self.pulses = 0.0
        self.min_delta = None
        self.max_delta = None
        self.complete = False


class PulseMeter:
    def __init__(self, meter):
        # Save the meter
        self.meter = meter

        # Keep track of the last pulse
        self.last_pulse = None

        # Create a record for each duration
        self.durations = []
        for duration in meter.durations:
            self.durations.append(PulseDurations(self, duration))


class PulseLogging:

    def __init__(self):
        # Initialize database
        self.db_instance = self.get_db(True)

        # Initialize durations
        self.pulse_meters = {}

    def get_db(self, force_connect=False):
        if force_connect or not self.db_instance:
            from config import configuration

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
                logger.error('Unable to establish database connection: %s' % exc.message)
                raise

        return self.db_instance

    def log_pulse(self, meter):
        # Save the current timestamp
        now = time.time()

        # Check if the meter exists
        pulse_meter = self.pulse_meters.get(meter.id)
        if pulse_meter:
            # Determine the duration between this pulse and the previous pulse
            delta = int((now - pulse_meter.last_pulse)*1000)

            # If the time has changed (i.e. clock adjustment due to NTP), then
            # we might get a negative time. In that case we should adjust the
            # delta again.
            if delta < 1:
                delta = 1
        else:
            # The pulse meter doesn't exist, so we create it.
            pulse_meter = self.pulse_meters[meter.id] = PulseMeter(meter)

            # Because there was no meter, we can't have a previous pulse
            delta = 0

        # Save the pulse into the database
        try:
            db = self.get_db()
            with closing(db.cursor()) as cur:
                # Insert the pulse record
                cur.execute("INSERT INTO `pulse_readings`(`meter_ref`,`timestamp`,`milli_sec`,`delta`) VALUES(%s,%s,%s,%s)", (meter.id, get_sql_timestamp(now), int(round(now * 1000)) % 1000, delta))

                # Log the actual pulse
                if delta > 0:
                    current_power = meter.get_current_from_delta(delta)
                    logger.debug('%s: Pulse written (delta=%.3fms, actual=%d%s)' % (meter.description, delta / 1000.0, current_power, meter.current_unit))
                else:
                    logger.debug('%s: Initial pulse written' % meter.description)

                # Update all durations
                for pulse_duration in pulse_meter.durations:
                    # Get the last known period
                    this_period = get_start_period(now, pulse_duration.duration)

                    # Normally a pulse has weight 1, unless it is distributed among multiple periods. Then
                    # the weight will be distributed evenly across these periods
                    pulse_weight = 1.0

                    # Check if we have moved to a new period
                    if not pulse_duration.period:
                        # Initialize the period
                        pulse_duration.period = this_period
                        pulse_duration.pulses = 0.0
                        pulse_duration.min_delta = pulse_duration.max_delta = None
                        pulse_duration.complete = False
                    else:
                        while this_period > pulse_duration.period:
                            # The period has passed, so this pulse should be distributed
                            # across the periods in-between.
                            period_pulse_duration = (pulse_duration.period + pulse_duration.duration) - pulse_meter.last_pulse
                            if period_pulse_duration > pulse_duration.duration:
                                period_pulse_duration = pulse_duration.duration

                            # Determine the pulse weight
                            period_pulse_weight = (period_pulse_duration * 1000.0) / delta

                            # Increment the number of pulses in this period based on the period that this
                            # pulse was inside the period
                            pulse_duration.pulses += period_pulse_weight

                            # This period's duration should be subtracted from the delta
                            pulse_weight -= period_pulse_weight

                            # Update min/max delta values
                            if not pulse_duration.min_delta or delta < pulse_duration.min_delta:
                                pulse_duration.min_delta = delta
                            if not pulse_duration.max_delta or delta > pulse_duration.max_delta:
                                pulse_duration.max_delta = delta

                            # If the pulse duration was complete, then we log it in the database
                            datetime = get_sql_timestamp(pulse_duration.period)
                            min_power = meter.get_current_from_delta(pulse_duration.max_delta) if pulse_duration.max_delta else 0.0
                            max_power = meter.get_current_from_delta(pulse_duration.min_delta) if pulse_duration.min_delta else 0.0
                            if pulse_duration.complete:
                                # Determine the usage based on the number of pulses
                                usage = meter.get_usage_from_pulses(pulse_duration.pulses)

                                # Determine the average power consumed in this period
                                avg_power = meter.get_current_from_pulses(pulse_duration.duration, pulse_duration.pulses)

                                # Determine the usage cost in this period. Note that the actual pulse might be in another
                                # period and this may have small differences
                                cost = meter.get_cost(get_cost_time(pulse_duration.period)) * usage

                                # Insert into the database
                                cur.execute("INSERT INTO `pulse_readings_per_duration`(`meter_ref`,`duration`,`timestamp`,`usage`,`min_power`,`max_power`,`cost`) VALUES(%s,%s,%s,%s,%s,%s,%s)", (meter.id, pulse_duration.duration, datetime, usage, min_power, max_power, cost))
                                logger.debug("%s: Pulse duration written (%s [%ds], usage %f%s (costs %f), avg %d%s, %d-%d%s)" % (meter.description, datetime, pulse_duration.duration, usage, meter.unit, cost, avg_power, meter.current_unit, min_power, max_power, meter.current_unit))
                            else:
                                logger.debug("%s: Incomplete duration record is not written (%s [%ds], %d-%d%s)" % (meter.description, datetime, pulse_duration.duration, min_power, max_power, meter.current_unit))

                            pulse_duration.period += pulse_duration.duration
                            pulse_duration.pulses = 0.0
                            pulse_duration.min_delta = pulse_duration.max_delta = None
                            pulse_duration.complete = True

                        # Increment the number of pulses
                        pulse_duration.pulses += pulse_weight

                        # Update min/max delta values
                        if not pulse_duration.min_delta or delta < pulse_duration.min_delta:
                            pulse_duration.min_delta = delta
                        if not pulse_duration.max_delta or delta > pulse_duration.max_delta:
                            pulse_duration.max_delta = delta

                # Commit changes
                db.commit()

        except Exception as exc:
            # Log error
            logger.error("Unable to log pulse to the database: %s." % exc.message)
            logger.error("Rendering current durations invalid for this meter")

            # Reset database
            self.db_instance = None

            # Reset complete status for the period
            for duration in pulse_meter.durations:
                duration.complete = False

        # Set the last pulse to the current pulse
        pulse_meter.last_pulse = now
