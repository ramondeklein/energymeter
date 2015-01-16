from ConfigParser import SafeConfigParser
import os

basedir = os.path.abspath(os.path.dirname(__file__))
config_file = os.path.join(basedir, 'energymeter.config')

configuration = SafeConfigParser()
configuration.read(config_file)
