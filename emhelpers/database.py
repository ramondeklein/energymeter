# Import modules
import MySQLdb
import logging

# Global definitions
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'struck'
MYSQL_DATABASE = 'metering'

# Setup logger
logger = logging.getLogger(__name__)


class Database(object):
    db_instance = None

    @staticmethod
    def instance():
        if not Database.db_instance:
            Database.db_instance = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
            Database.db_instance.cursor().execute("SET time_zone = '+0:00'")
        return Database.db_instance

    @staticmethod
    def cursor():
        return Database.instance().cursor()

    @staticmethod
    def commit():
        return Database.instance().commit()
