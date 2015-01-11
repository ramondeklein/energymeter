from app import app

# Import modules
import math, datetime, dateutil.parser
from flask import request, jsonify
from emhelpers import Database

def to_sql_utc(dt, precision):
  # If there is no timezone specified, then we convert it from local time
  if not dt.tzinfo:
      dt = dt.replace(tzinfo=dateutil.tz.tzlocal())

  # Round on the proper precision
  dt = dt.replace(microsecond=int(round(float(dt.microsecond) / 1000000, precision) * 1000000))

  # Convert back to UTC
  return dt.astimezone(dateutil.tz.tzutc())

def from_sql_utc(dt, precision = 0):
  # Format with the proper precision
  dt = dt.replace(tzinfo=None)
  if precision != 6 and dt.microsecond:
      if precision == 0:
          dt = dt.replace(microsecond=0)
      else:
        return dt.replace(tzinfo=None).isoformat()[:precision-6].rstrip('0') + 'Z'
  return dt.replace(tzinfo=None).isoformat() + 'Z'

def get_period(precision):
  # Determine the start and end parameters (optional)
  argStart = request.args.get('start')
  argEnd = request.args.get('end')

  # Convert the start and end to Python types
  start = dateutil.parser.parse(argStart) if argStart else None
  end = dateutil.parser.parse(argEnd) if argEnd else None

  # Convert defaults for start/end (default is last day and otherwise we select an entire day)
  if not start and not end:
    end = datetime.datetime.now(dateutil.tz.tzutc())
  if not start and end:
    start = end - datetime.timedelta(days=1)
  elif start and not end:
    end = start + datetime.timedelta(days=1)

  # If there is no timezone specified, then we convert it from local time
  start = to_sql_utc(start, precision)
  end = to_sql_utc(end, precision)

  # Convert datetime to UTC
  return {
    "utcStart": start,
    "utcEnd": end
  }

@app.route("/api/v1/pulses/<int:meter_id>")
def get_pulses(meter_id):
  # Obtain the period
  precision = 3
  period = get_period(precision)
  utcStart = period['utcStart']
  utcEnd = period['utcEnd']

  # Obtain pulse readings
  cur = Database.cursor()
  cur.execute("SELECT timestamp, delta FROM pulse_readings WHERE timestamp >= %s AND timestamp < %s ORDER BY timestamp", (utcStart, utcEnd));
  rows = cur.fetchall()
  return jsonify({
    'start': from_sql_utc(utcStart, precision),
    'end': from_sql_utc(utcEnd, precision),
    'pulses': map(lambda r: [from_sql_utc(r[0], precision), r[1]], rows)
  })

@app.route("/api/v1/pulses/<int:meter_id>/<int:duration>")
def get_duration(meter_id, duration):
  # Obtain the period
  precision = 3
  period = get_period(precision)
  utcStart = period['utcStart']
  utcEnd = period['utcEnd']

  # Obtain duration readings
  cur = Database.cursor()
  cur.execute("SELECT timestamp, pulses FROM pulse_readings_per_duration WHERE timestamp >= %s AND timestamp < %s ORDER BY timestamp", (utcStart, utcEnd));
  rows = cur.fetchall()
  return jsonify({
    'start': from_sql_utc(utcStart, precision),
    'end': from_sql_utc(utcEnd, precision),
    'pulses': map(lambda r: [from_sql_utc(r[0], precision), r[1]], rows)
  })
