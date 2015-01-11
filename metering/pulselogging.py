from emhelpers import Database
import time, datetime
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

  def add_meter(self, meterId, description):
    meter = self.meters[meterId] = {
      'lastPulse': 0,
      'description': description
    }
    for duration in self.durations:
      meter[duration] = { 
        'lastPeriod': None,
        'periodsCounted': 0
      }
      # TODO: Add a timer to make sure the pulses are flushed when the meter is (almost) not triggering

  def log_pulse(self, meterId, increment):
    # Save the current timestamp
    now = time.time()

    # Determine the delta between the pulses
    meter = self.meters[meterId]

    # Now can be before lastPulse if the clock is adjusted
    lastPulse = meter['lastPulse']
    if lastPulse:
      delta = int((now - lastPulse)*1000) if now > lastPulse else 0
    else:
      delta = 0
    meter['lastPulse'] = now

    # Save the pulse into the database
    cur = Database.cursor()
    print now
    cur.execute("INSERT INTO pulse_readings(meter_ref,timestamp,delta) VALUES(%s,NOW(3),%s)", (meterId, delta));
    logger.debug("Pulse written (meter={}[{}], delta={})".format(meter['description'], meterId, delta))

    # Save all durations
    for duration in self.durations:
      meterDuration = meter[duration]
      lastPeriod = meterDuration['lastPeriod']
      currentPeriod = get_period(now, duration)
      if lastPeriod and (lastPeriod == currentPeriod):
        # Increment the number of pulses
        meterDuration['pulses'] = meterDuration['pulses']+increment
      else:
        # If we had a previous period, then it's complete now and we can save it. We don't
	# save the first counted period, because it will probably be incomplete.
        if lastPeriod:
          pulses = meterDuration['pulses']
          if meterDuration['periodsCounted'] > 0:
            cur.execute("INSERT INTO pulse_readings_per_duration(meter_ref,duration,timestamp,pulses) VALUES(%s,%s,%s,%s)", (meterId, duration, lastPeriod, pulses));
            logger.debug("Pulse duration written (meter={}[{}], timestamp={} [duration:{}], pulses={})".format(meter['description'], meterId, lastPeriod, duration, pulses))
          else:
            logger.debug("First pulse duration not written (meter={}[{}], timestamp={} [duration:{}], pulses={})".format(meter['description'], meterId, lastPeriod, duration, pulses))
          meterDuration['periodsCounted'] = meterDuration['periodsCounted']+1

        # Initialize the new period
        meterDuration['lastPeriod'] = currentPeriod
        meterDuration['pulses'] = increment

    # Commit changes
    Database.commit()
