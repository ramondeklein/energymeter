from app import app

# Import modules
import datetime, dateutil.parser
from flask import request, jsonify
from emhelpers import Database

def getSqlUtcDateTime(dt):
  # If there is no timezone specified, then we convert it from local time
  if not dt.tzinfo:
      dt = dt.replace(tzinfo=dateutil.tz.tzlocal())

  # Round the datetime to a SQL compatible structure (without ms)
  if end.microsecond > 0:
    end = end.replace(microsecond=0) + datetime.timedelta(seconds=1)

  # Convert back to UTC
  dt.astimezone(dateutil.tz.tzutc())
  return dt

def get_period():
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
  if not start.tzinfo:
      start = start.replace(tzinfo=dateutil.tz.tzlocal())
  if not end.tzinfo:
      end = end.replace(tzinfo=dateutil.tz.tzlocal())

  # Make sure we align to the second
  if start.microsecond > 0:
      start = start.replace(microsecond=0)
  if end.microsecond > 0:
    end = end.replace(microsecond=0) + datetime.timedelta(seconds=1)

  # Convert datetime to UTC
  return {
    "utcStart": start.astimezone(dateutil.tz.tzutc()),
    "utcEnd": end.astimezone(dateutil.tz.tzutc())
  }

@app.route("/api/v1/pulses/<int:meter_id>")
def get_pulses(meter_id):
  # Obtain the period
  period = get_period()
  utcStart = period['utcStart']
  utcEnd = period['utcEnd']

  # Obtain pulse readings
  cur = Database.cursor()
  cur.execute("SELECT timestamp, delta FROM pulse_readings WHERE timestamp >= %s AND timestamp < %s ORDER BY timestamp", (utcStart, utcEnd));
  rows = cur.fetchall()
  return jsonify({
    'start': utcStart.replace(tzinfo=None).isoformat() + 'Z',
    'end': utcEnd.replace(tzinfo=None).isoformat() + 'Z',
    'pulses': map(lambda r: [r[0].isoformat() + 'Z', r[1]], rows)
  })

@app.route("/api/v1/pulses/<int:meter_id>/<int:duration>")
def get_duration(meter_id, duration):
  # Obtain the period
  period = get_period()
  utcStart = period['utcStart']
  utcEnd = period['utcEnd']

  # Obtain duration readings
  cur = Database.cursor()
  cur.execute("SELECT timestamp, pulses FROM pulse_readings_per_duration WHERE timestamp >= %s AND timestamp < %s ORDER BY timestamp", (utcStart, utcEnd));
  rows = cur.fetchall()
  return jsonify({
    'start': utcStart.isoformat(),
    'end': utcEnd.isoformat(),
    'pulses': map(lambda r: [r[0].isoformat() + 'Z', r[1]], rows)
  })
