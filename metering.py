#!/usr/bin/python
from log import initialize_logging, logging
from config import configuration
from meter import Meter
from pulselogging import PulseLogging

pl = PulseLogging()

# Obtain the name of the logfile
initialize_logging('metering')

# Setup logger
logger = logging.getLogger(__name__)


def pulse_callback(meter):
    # Log the pulse
    pl.log_pulse(meter)


def init():
    # Check if simulation is enabled
    simulation = configuration.has_option('metering', 'simulation') and configuration.getboolean('metering', 'simulation')

    # Initialize GPIO if not running in simulation mode
    if not simulation:
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
        except RuntimeError:
            logger.error("Unable to import RPi.GPIO. Make sure you run this script with root privileges.")
            raise

    meters = []
    try:
        # Setup all meters
        meter_index = 0
        for section in configuration.sections():
            items = section.split(':')
            if (len(items) is 2) and items[0] == 'meter':
                try:
                    # Create the meter
                    meter = Meter(section)

                    # Check if the meter is enabled
                    if meter.enabled:
                        if not simulation:
                            logger.debug('Initializing GPIO for meter %d "%s"' % (meter.id, meter.description))
                            meter.init_gpio(pulse_callback)
                        else:
                            meter.simulation_key = chr(ord('1') + meter_index)

                        # Append the meter to the list
                        meters.append(meter)

                        # Next meter
                        meter_index += 1

                except Exception as exc:
                    logger.error('Error during configuration of meters: %s' % exc.message)

        if not simulation:
            # TODO: Wait for SIGINT
            import time
            while True:
                time.sleep(1000)
        else:
            from terminal import getch

            # Show that we're logging events
            print 'Logging events until \'q\' is pressed'
            for meter in meters:
                print '- %s: %s' % (meter.simulation_key, meter.description)

            # Repeat until 'q' is pressed
            ch = getch()
            while ch != 'q':
                # Find the meter
                for meter in meters:
                    if meter.simulation_key == ch:
                        pl.log_pulse(meter)
                ch = getch()
    finally:
        if not simulation:
            GPIO.cleanup()


# Initialize
init()
