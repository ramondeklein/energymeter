from server import app

# Import modules
import datetime
import dateutil.parser
from flask import request, jsonify
from emhelpers import Database

epoch = datetime.datetime.utcfromtimestamp(0)

def to_sql_utc(dt, precision):
    # If there is no timezone specified, then we convert it from local time
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=dateutil.tz.tzlocal())

    # Round on the proper precision
    dt = dt.replace(microsecond=int(round(float(dt.microsecond) / 1000000, precision) * 1000000))

    # Convert back to UTC
    return dt.astimezone(dateutil.tz.tzutc())


def from_sql_utc(dt):
    dt = dt.replace(tzinfo=None)
    return (dt - epoch).total_seconds() * 1000

def get_period(precision):
    # Determine the start and end parameters (optional)
    arg_start = request.args.get('start')
    arg_end = request.args.get('end')

    # Convert the start and end to Python types
    start = dateutil.parser.parse(arg_start) if arg_start else None
    end = dateutil.parser.parse(arg_end) if arg_end else None

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
    return [start, end]


@app.route("/api/v1/pulses/<int:meter_id>")
def get_pulses(meter_id):
    # Obtain the period
    precision = 3
    [utc_start, utc_end] = get_period(precision)

    # Obtain pulse readings
    cur = Database.cursor()
    cur.execute("SELECT timestamp, delta FROM pulse_readings WHERE timestamp >= %s AND timestamp < %s ORDER BY timestamp", (utc_start, utc_end));
    rows = cur.fetchall()
    return jsonify({
        'start': from_sql_utc(utc_start),
        'end': from_sql_utc(utc_end),
        'pulses': map(lambda r: [from_sql_utc(r[0]), r[1]], rows)
    })


@app.route("/api/v1/pulses/<int:meter_id>/<int:duration>")
def get_duration(meter_id, duration):
    # Obtain the period
    precision = 0
    [utc_start, utc_end] = get_period(precision)

    # Obtain duration readings
    cur = Database.cursor()
    cur.execute("SELECT timestamp, pulses FROM pulse_readings_per_duration WHERE timestamp >= %s AND timestamp < %s ORDER BY timestamp", (utc_start, utc_end));
    rows = cur.fetchall()
    return jsonify({
        'start': from_sql_utc(utc_start),
        'end': from_sql_utc(utc_end),
        'pulses': map(lambda r: [from_sql_utc(r[0]), r[1]], rows)
    })
