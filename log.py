from config import configuration
import logging
import os


def initialize_logging(section):
    # Default is no log warnings
    log_warnings = []

    # Determine the logfile
    log_file = configuration.get(section, 'logfile') if configuration.has_option(section, 'logfile') else None

    # Determine the log level
    log_level_text = configuration.get(section, 'loglevel') if configuration.has_option(section, 'loglevel') else 'INFO'
    log_level_text = log_level_text.lower()
    if log_level_text == 'debug':
        log_level = logging.DEBUG
    elif log_level_text == 'info':
        log_level = logging.INFO
    elif log_level_text == 'warn':
        log_level = logging.WARN
    elif log_level_text == 'error':
        log_level = logging.ERROR
    else:
        log_warnings.append('[{}] has invalid loglevel "{}" (reverting to INFO level).'.format(section, log_level_text))
        log_level_text = 'info'
        log_level = logging.INFO

    # Check if a logfile is specified
    if log_file:
        # Make sure the directory exists
        log_file = os.path.abspath(log_file)
        log_directory = os.path.dirname(log_file)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        # Configure the logging
        logging.basicConfig(format='%(asctime)s:%(thread)d:%(levelname)s:%(message)s', filename=log_file, level=log_level)
    else:
        # Configure the logging
        logging.basicConfig(format='%(asctime)s:%(thread)d:%(levelname)s:%(message)s', level=log_level)

    # Obtain the logger
    logger = logging.getLogger(__name__)
    logger.info('Starting (using level {})'.format(log_level_text.upper()))

    # Log warnings
    for warning in log_warnings:
        logger.warn(warning)
