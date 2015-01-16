from config import configuration
from log import logging

# Import modules
import MySQLdb
import time
import datetime
import dateutil.parser
from contextlib import closing
from flask import request, jsonify

# Setup logger
logger = logging.getLogger(__name__)

# Determine epoch
epoch = datetime.datetime.utcfromtimestamp(0)


def get_db():
    # Determine the current configuration
    hostname = configuration.get('database', 'hostname') if configuration.has_option('database', 'hostname') else 'localhost'
    port = configuration.getint('database', 'port') if configuration.has_option('database', 'port') else 2206
    username = configuration.get('database', 'username') if configuration.has_option('database', 'username') else 'root'
    password = configuration.get('database', 'password') if configuration.has_option('database', 'password') else ''
    database = configuration.get('database', 'database') if configuration.has_option('database', 'database') else 'energymeter'

    try:
        # Connect to the database
        db_instance = MySQLdb.connect(host=hostname, port=port, user=username, passwd=password, db=database)

        # Always use UTC
        db_instance.cursor().execute("SET time_zone = '+0:00'")
        return db_instance
    except Exception as exc:
        logger.error('Unable to establish database connection: %s' % (exc.message))
        raise

def get_sql_timestamp(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def from_sql_utc(dt):
    dt = dateutil.parser.parse(dt)
    dt = dt.replace(tzinfo=None)
    return (dt - epoch).total_seconds() * 1000


def get_period():
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
    start = get_sql_timestamp(start)
    end = get_sql_timestamp(end)

    # Convert datetime to UTC
    return [start, end]


def init_api(app):
    @app.route("/api/v1/pulses/<int:meter_id>")
    def get_pulses(meter_id):
        # Obtain the period
        [utc_start, utc_end] = get_period()

        # Obtain pulse readings
        with closing(get_db().cursor()) as cur:
            cur.execute("SELECT timestamp, delta FROM pulse_readings WHERE meter_ref = %s AND timestamp >= %s AND timestamp < %s ORDER BY timestamp", (meter_id, utc_start, utc_end));
            rows = cur.fetchall()
            return jsonify({
                'start': from_sql_utc(utc_start),
                'end': from_sql_utc(utc_end),
                'pulses': map(lambda r: [from_sql_utc(r[0]), r[1]], rows)
            })


    @app.route("/api/v1/pulses/<int:meter_id>/<int:duration>")
    def get_pulses_by_duration(meter_id, duration):
        # Obtain the period
        precision = 0
        [utc_start, utc_end] = get_period(precision)

        # Obtain duration readings
        with closing(get_db().cursor()) as cur:
            cur.execute("SELECT timestamp, pulses FROM pulse_readings_per_duration WHERE meter_ref = %s AND duration = %s timestamp >= %s AND timestamp >= %s AND timestamp < %s ORDER BY timestamp", (meter_id, duration, utc_start, utc_end));
            rows = cur.fetchall()
            return jsonify({
                'start': from_sql_utc(utc_start),
                'end': from_sql_utc(utc_end),
                'pulses': map(lambda r: [from_sql_utc(r[0]), r[1]], rows)
            })
