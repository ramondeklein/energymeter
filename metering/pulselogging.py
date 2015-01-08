from helpers import Database
import time, datetime

def get_period(now, duration):
  gm_time = time.gmtime(now)
  seconds = (((gm_time.tm_hour * 60) + gm_time.tm_min) * 60) + gm_time.tm_sec
  start_seconds = int(seconds / duration) * duration
  print int(start_seconds / (24*60))
  period = datetime.datetime(gm_time.tm_year, gm_time.tm_mon, gm_time.tm_mday, int(start_seconds / (60*60)), int(start_seconds / 60) % 60, start_seconds % 60)
  print period
  return period

class PulseLogging:
  def __init__(self):
    self.meters = {}
    self.durations = [60, 300, 3600]

  def log_pulse(self, meterId):
    # Save the current timestamp
    now = time.time()

    # Determine the delta between the pulses
    meter = self.meters[meterId] if meterId in self.meters.keys() else None
    if meter:
      # Now can be before lastPulse if the clock is adjusted
      lastPulse = meter['lastPulse']
      delta = int((now - lastPulse)*1000) if now > lastPulse else 0
    else:
      meter = self.meters[meterId] = {}
      for duration in self.durations:
        meter[duration] = { 
          'lastPeriod': None
        }
      delta = 0
    meter['lastPulse'] = now

    # Save the pulse into the database
    cur = Database.cursor()
    cur.execute("INSERT INTO pulse_readings(meter_ref,timestamp,delta) VALUES(%s,NOW(),%s)", (meterId, delta));

    # Save all durations
    for duration in self.durations:
      meterDuration = meter[duration]
      lastPeriod = meterDuration['lastPeriod']
      currentPeriod = get_period(now, duration)
      if lastPeriod and (lastPeriod == currentPeriod):
        # Increment the number of pulses
        meterDuration['pulses'] = meterDuration['pulses']+1
      else:
        # If we had a previous period, then it's complete now and we can save it
        if lastPeriod:
          cur.execute("INSERT INTO pulse_readings_per_duration(meter_ref,duration,timestamp,pulses) VALUES(%s,%s,NOW(),%s)", (meterId, duration, meterDuration['pulses']));

        # Initialize the new period
        meterDuration['lastPeriod'] = currentPeriod
        meterDuration['pulses'] = 1

    # Commit changes
    Database.commit()
