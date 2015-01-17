from config import configuration
from log import logging

# Import modules
import MySQLdb
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
    dt = dt.replace(tzinfo=None)
    return int((dt - epoch).total_seconds() * 1000)


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

def find_meters(meter_id=None):
    from config import configuration
    from meter import Meter

    meters = []
    for section in configuration.sections():
        items = section.split(':')
        if (len(items) is 2) and items[0] == 'meter':
            if not meter_id or (int(items[1]) == meter_id):
                meter = Meter(section)
                meters.append({
                    'id': meter.id,
                    'description': meter.description
                })
    return meters

def init_api(app):

    @app.route("/api/v1/meter")
    def get_meters():
        return jsonify({'meters': find_meters()})

    @app.route("/api/v1/meter/<int:meter_id>")
    def get_meter(meter_id):
        meters = find_meters(meter_id)
        if len(meters) > 0:
            return jsonify({'meter': meters[0]})
        else:
            return jsonify({})

    @app.route("/api/v1/pulses/<int:meter_id>")
    def get_pulses(meter_id):
        # Obtain the period
        [utc_start, utc_end] = get_period()

        # Obtain pulse readings
        with closing(get_db().cursor()) as cur:
            cur.execute("SELECT timestamp, power FROM pulse_readings WHERE meter_ref = %s AND timestamp >= %s AND timestamp < %s ORDER BY timestamp", (meter_id, utc_start, utc_end));
            rows = cur.fetchall()
            nr_of_rows = len(rows)
            return jsonify({
                'start': from_sql_utc(rows[0][0]) if utc_start else utc_start,
                'end': from_sql_utc(rows[nr_of_rows-1][0]) if utc_start else utc_start,
                'data': map(lambda r: [from_sql_utc(r[0]), r[1]], rows)
            })

    @app.route("/api/v1/duration/<int:meter_id>/<int:duration>")
    def get_pulses_by_duration(meter_id, duration):
        # Obtain the period
        [utc_start, utc_end] = get_period()

        # Obtain duration readings
        with closing(get_db().cursor()) as cur:
            cur.execute("SELECT timestamp, avg_power FROM pulse_readings_per_duration WHERE meter_ref = %s AND duration = %s AND timestamp >= %s AND timestamp < %s ORDER BY timestamp", (meter_id, duration, utc_start, utc_end));
            rows = cur.fetchall()
            nr_of_rows = len(rows)
            return jsonify({
                'start': from_sql_utc(rows[0][0]) if utc_start else utc_start,
                'end': from_sql_utc(rows[nr_of_rows-1][0]) if utc_start else utc_start,
                'data': map(lambda r: [from_sql_utc(r[0]), r[1]], rows)
            })

    @app.route("/api/v1/extduration/<int:meter_id>/<int:duration>")
    def get_pulses_by_duration_ext(meter_id, duration):
        # Obtain the period
        [utc_start, utc_end] = get_period()

        # Obtain duration readings
        with closing(get_db().cursor()) as cur:
            cur.execute("SELECT timestamp, min_power, avg_power, max_power FROM pulse_readings_per_duration WHERE meter_ref = %s AND duration = %s AND timestamp >= %s AND timestamp < %s ORDER BY timestamp", (meter_id, duration, utc_start, utc_end));
            rows = cur.fetchall()
            nr_of_rows = len(rows)
            return jsonify({
                'start': from_sql_utc(rows[0][0]) if utc_start else utc_start,
                'end': from_sql_utc(rows[nr_of_rows-1][0]) if utc_start else utc_start,
                'data': map(lambda r: [from_sql_utc(r[0]), r[1], r[2], r[3]], rows)
            })
