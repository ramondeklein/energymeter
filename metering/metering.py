#!/usr/bin/python

# Setup logging
import logging
logging.basicConfig(format='%(asctime)s:%(thread)d:%(levelname)s:%(message)s', filename='metering.log', level=logging.DEBUG)

# Setup logger
logger = logging.getLogger(__name__)

# Extend module search path
import sys
sys.path.append('..')

# Import modules
from emhelpers import Database, Settings, getch
from pulselogging import PulseLogging

# Check if we're running in simulation mode
liveMode = Settings.get_bool('metering:live_mode')

# Import the GPIO module when not running in simulation
if liveMode:
    logger.info('Running in live mode')
    try:
        import RPi.GPIO as GPIO
    except RuntimeError:
        print("Error importing RPi.GPIO. Make sure you run this script with root privileges.")
else:
    logger.info('Running in simulation mode (use keyboard to generate pulses).')

# Global variables
pulseLogging = PulseLogging()
pinInfoDict = {}
keyInfoDict = {}


def setup_pins():
    if liveMode:
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)

    # Iterate over each meter
    cur = Database.cursor()
    cur.execute("SELECT id, pin, description, bounce_time, input_type, event_type FROM meters")
    rows = cur.fetchall()

    key = '1'
    for rows in rows:
        # Obtain the individual items
        id = rows[0]
        pin = rows[1]
        description = rows[2]
        bounce_time = rows[3]
        input_type = rows[4]
        event_type = rows[5]

        # Save info in the dictionary
        if liveMode and (pin >= 0):
            pinInfoDict[pin] = { 'meter': id, 'description': description }

            # Setup callbacks
            def cb_gpio_callback(channel):
                pinInfo = pinInfoDict[channel]
                pulseLogging.log_pulse(pinInfo['meter'],1)

            # Determine the pull-up/down setting
            if input_type == 1:
                pull_up_down = GPIO.PUD_DOWN
                pull_up_down_str = 'pull-down'
            elif input_type == 2:
                pull_up_down = GPIO.PUD_UP
                pull_up_down_str = 'pull-up'
            else:
                pull_up_down = GPIO.PUD_OFF
                pull_up_down_str = 'no pull-up/down'

            # Determine the event-type
            if event_type == 1:
                edge = GPIO.RISING
                edge_str = 'rising edge'
            elif input_type == 2:
                edge = GPIO.FALLING
                edge_str = 'falling edge'
            else:
                edge = GPIO.BOTH
                edge_str = 'both edges'
            GPIO.setup(pin, GPIO.IN, pull_up_down=pull_up_down)
            if bounce_time > 0:
                GPIO.add_event_detect(pin, edge, callback=cb_gpio_callback, bouncetime=bounce_time)
            else:
                GPIO.add_event_detect(pin, edge, callback=cb_gpio_callback)
            logger.info('{}: Pin {}, {}, {}, bounce: {}ms'.format(description, pin, pull_up_down_str, edge_str, bounce_time))

        # Assign a key to the meter
        keyInfoDict[key] = { 'meter': id, 'description': description }
        key = chr(ord(key) + 1)

        pulseLogging.add_meter(id, description)


def free_pins():
    if liveMode:
        for pin in pinInfoDict:
            GPIO.remove_event_detect(pin)
        GPIO.cleanup()

# Setup all pins
setup_pins()

# Handle all keystrokes, until 'q' is typed
if liveMode:
  import time
  while True:
    time.sleep(1000);
else:
  logger.info('Logging events until \'q\' is pressed')
  ch = getch()
  while ch != 'q':
    if ch in keyInfoDict:
      keyInfo = keyInfoDict[ch]
      logger.info('Pulse "' + keyInfo['description'] + '" simulated.')
      pulseLogging.log_pulse(keyInfo['meter'],1)
    ch = getch()

# Free the pins
free_pins()
