from emhelpers import Database
import time
import datetime
import logging

# Setup logger
logger = logging.getLogger(__name__)


def get_period(now, duration):
    gm_time = time.gmtime(now)
    seconds = (((gm_time.tm_hour * 60) + gm_time.tm_min) * 60) + gm_time.tm_sec
    start_seconds = int(seconds / duration) * duration
    return datetime.datetime(gm_time.tm_year, gm_time.tm_mon, gm_time.tm_mday, int(start_seconds / (60*60)), int(start_seconds / 60) % 60, start_seconds % 60)


class PulseLogging:
    def __init__(self):
        self.meters = {}
        self.durations = [60, 5 * 60, 15 * 60, 60 * 60]

    def add_meter(self, meter_id, description):
        meter = self.meters[meter_id] = {
            'last_pulse': 0,
            'description': description
        }
        for duration in self.durations:
            meter[duration] = {
                'last_period': None,
                'periods_counted': 0
            }
            # TODO: Add a timer to make sure the pulses are flushed when the meter is (almost) not triggering

    def log_pulse(self, meter_id, increment):
        # Save the current timestamp
        now = time.time()

        # Determine the delta between the pulses
        meter = self.meters[meter_id]

        # Now can be before lastPulse if the clock is adjusted
        last_pulse = meter['last_pulse']
        if last_pulse:
            delta = int((now - last_pulse)*1000) if now > last_pulse else 0
        else:
            delta = 0
        meter['last_pulse'] = now

        # Save the pulse into the database
        cur = Database.cursor()
        cur.execute("INSERT INTO pulse_readings(meter_ref,timestamp,delta) VALUES(%s,NOW(3),%s)", (meter_id, delta))
        logger.debug("Pulse written (meter={}[{}], delta={})".format(meter['description'], meter_id, delta))

        # Save all durations
        for duration in self.durations:
            meter_duration = meter[duration]
            last_period = meter_duration['last_period']
            current_period = get_period(now, duration)
            if last_period and (last_period == current_period):
                # Increment the number of pulses
                meter_duration['pulses'] = meter_duration['pulses']+increment
            else:
                # If we had a previous period, then it's complete now and we can save it. We don't
                # save the first counted period, because it will probably be incomplete.
                if last_period:
                    pulses = meter_duration['pulses']
                    if meter_duration['periodsCounted'] > 0:
                        cur.execute("INSERT INTO pulse_readings_per_duration(meter_ref,duration,timestamp,pulses) VALUES(%s,%s,%s,%s)", (meter_id, duration, lastPeriod, pulses));
                        logger.debug("Pulse duration written (meter={}[{}], timestamp={} [duration:{}], pulses={})".format(meter['description'], meter_id, lastPeriod, duration, pulses))
                    else:
                        logger.debug("First pulse duration not written (meter={}[{}], timestamp={} [duration:{}], pulses={})".format(meter['description'], meter_id, lastPeriod, duration, pulses))
                    meter_duration['periodsCounted'] += 1

                # Initialize the new period
                meter_duration['last_period'] = current_period
                meter_duration['pulses'] = increment

        # Commit changes
        Database.commit()
