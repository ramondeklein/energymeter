#!/usr/bin/python

# Setup logging
import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)

# Setup logger
logger = logging.getLogger(__name__)

# Extend module search path
import sys
sys.path.append('..')

# Import modules
import datetime, dateutil.parser, pytz
from flask import Flask, request, jsonify
from helpers import Database

# Declare Flask application
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

def get_period():
  # Determine the start and end parameters (optional)
  argStart = request.args.get('start')
  argEnd = request.args.get('end')

  # Convert the start and end to Python types
  start = dateutil.parser.parse(argStart) if argStart else None
  end = dateutil.parser.parse(argEnd) if argEnd else None

  # Convert defaults for start/end (default is last day and otherwise we select an entire day)
  if not start and not end:
    end = datetime.datetime.now(pytz.utc)
  if not start and end:
    start = end - datetime.timedelta(days=1)
  elif start and not end:
    end = start + datetime.timedelta(days=1)

  # Convert datetime to UTC
  return {
    "utcStart": start.astimezone(pytz.utc),
    "utcEnd": end.astimezone(pytz.utc)
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
    'start': utcStart.isoformat(),
    'end': utcEnd.isoformat(),
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

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80, debug=True)
