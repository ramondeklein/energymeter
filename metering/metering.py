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
from emhelpers import Database, Settings, getch
from pulselogging import PulseLogging

# Check if we're running in simulation mode
liveMode = Settings.get_bool('metering:live_mode')

# Import the GPIO module when not running in simulation
if liveMode:
  import RPi.GPIO as GPIO
  logger.info('Running in live mode')
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
  cur.execute("SELECT id, pin, description, bounce_time, pulse_value FROM meters")
  rows = cur.fetchall()

  key = '1'
  for rows in rows:
    # Obtain the individual items
    id = rows[0]
    pin = rows[1]
    description = rows[2]
    bounce_time = rows[3]
    pulse_value = rows[4]

    # Save info in the dictionary
    if liveMode and (pin >= 0):
      pinInfoDict[pin] = { 'meter': id, 'description': description }

      # Setup callbacks
      def cbGpioCallback(channel):
        pinInfo = pinInfoDict[channel]
        pulseLogging.log_pulse(pinInfo['meter'],1)

      # Initialize GPIO pins (TODO: Add FALLING/RAISING support)
      GPIO.setup(pin, GPIO.IN)
      GPIO.add_event_detect(pin, GPIO.FALLING, callback=cbGpioCallback, bouncetime = bounce_time)

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
ch = getch()
while ch != 'q':
  if ch in keyInfoDict:
    keyInfo = keyInfoDict[ch]
    logger.info('Pulse "' + keyInfo['description'] + '" simulated.')
    pulseLogging.log_pulse(keyInfo['meter'],1)
  ch = getch()

# Free the pins
free_pins()
