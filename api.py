from config import configuration
from log import logging

# Import modules
import MySQLdb
import datetime
import time
import dateutil.parser
from contextlib import closing
from flask import request, jsonify
from config import configuration
from meter import Meter

# Setup logger
logger = logging.getLogger(__name__)

# Determine epoch
epoch = datetime.datetime.utcfromtimestamp(0)

# Obtain the list of all meters
meters = {}
for section in configuration.sections():
    items = section.split(':')
    if (len(items) is 2) and items[0] == 'meter':
        meter = Meter(section)
        meters[meter.id] = meter


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


def init_api(app):

    @app.route("/api/v1/meter")
    def get_meters():
        return jsonify({'meters': map(lambda (k,m): {
                'id': m.id,
                'description': m.description,
                'unit': m.unit,
                'currentFactor': m.current_factor,
                'currentUnit': m.current_unit,
                'durations': m.durations
            }, meters.iteritems())})

    @app.route("/api/v1/pulses/<int:meter_id>")
    def get_pulses(meter_id):
        # Obtain the period
        [utc_start, utc_end] = get_period()

        # Obtain pulse readings
        with closing(get_db().cursor()) as cur:
            cur.execute("SELECT `timestamp`, `power` FROM `pulse_readings` WHERE `meter_ref` = %s AND `timestamp` >= %s AND `timestamp` < %s ORDER BY `timestamp`", (meter_id, utc_start, utc_end))
            rows = cur.fetchall()
            nr_of_rows = len(rows)
            return jsonify({
                'start': from_sql_utc(rows[0][0]) if utc_start else utc_start,
                'end': from_sql_utc(rows[nr_of_rows-1][0]) if utc_start else utc_start,
                'data': map(lambda r: [from_sql_utc(r[0]), r[1]], rows)
            })

    @app.route("/api/v1/usage/<int:meter_id>/<int:duration>")
    def get_usage_by_duration(meter_id, duration):
        # Obtain the period
        [utc_start, utc_end] = get_period()

        # Obtain duration readings
        with closing(get_db().cursor()) as cur:
            cur.execute("SELECT `timestamp`, `usage` FROM `pulse_readings_per_duration` WHERE `meter_ref` = %s AND `duration` = %s AND `timestamp` >= %s AND `timestamp` < %s ORDER BY `timestamp`", (meter_id, duration, utc_start, utc_end))
            rows = cur.fetchall()
            nr_of_rows = len(rows)
            return jsonify({
                'start': from_sql_utc(rows[0][0]) if nr_of_rows > 0 else utc_start,
                'end': from_sql_utc(rows[nr_of_rows-1][0]) if nr_of_rows > 0 else utc_start,
                'data': map(lambda r: [from_sql_utc(r[0]), r[1]], rows)
            })

    @app.route("/api/v1/cost/<int:meter_id>/<int:duration>")
    def get_cost_by_duration(meter_id, duration):
        # Obtain the period
        [utc_start, utc_end] = get_period()

        # Obtain duration readings
        with closing(get_db().cursor()) as cur:
            cur.execute("SELECT `timestamp`, `cost` FROM `pulse_readings_per_duration` WHERE `meter_ref` = %s AND `duration` = %s AND `timestamp` >= %s AND `timestamp` < %s ORDER BY `timestamp`", (meter_id, duration, utc_start, utc_end))
            rows = cur.fetchall()
            nr_of_rows = len(rows)
            return jsonify({
                'start': from_sql_utc(rows[0][0]) if nr_of_rows > 0 else utc_start,
                'end': from_sql_utc(rows[nr_of_rows-1][0]) if nr_of_rows > 0 else utc_start,
                'data': map(lambda r: [from_sql_utc(r[0]), r[1]], rows)
            })

    @app.route("/api/v1/readings/last")
    def get_last_readings():
        # Obtain duration readings
        with closing(get_db().cursor()) as cur:
            # TODO: FIX THIS ONE, BECAUSE WE SHOULD ALSO CONSIDER THE MILLISECONDS
            cur.execute("SELECT `pr`.`meter_ref`, `pr`.`timestamp`, `pr`.`milli_sec`, `pr`.`delta` FROM (SELECT `meter_ref`, MAX(`timestamp`) AS `max_timestamp` FROM `pulse_readings` GROUP BY `meter_ref`) `pr_last` INNER JOIN `pulse_readings` `pr` ON `pr_last`.`meter_ref` = `pr`.`meter_ref` AND `pr_last`.`max_timestamp` = `pr`.`timestamp`")
            rows = cur.fetchall()

            # If the duration between the last pulse and the current moment is longer then
            # the previous pulse, then update the actual power. Although this reading is
            # not 100% correct, it's better then the last known value.
            now = time.time()

            def convert(row):
                last_delta = row[3]
                last_timestamp = (from_sql_utc(row[1]) + row[2]) / 1000.0
                this_delta = now - last_timestamp
                return {
                    'id': row[0],
                    'power': meters[row[0]].get_current_from_delta(this_delta if this_delta > last_delta else last_delta)

                }

            # Return the meter data
            return jsonify({
                'meters': map(convert, rows)
            })
