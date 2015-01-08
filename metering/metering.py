#!/usr/bin/python

# Setup logging
import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)

# Setup logger
logger = logging.getLogger(__name__)

# Import modules
from helpers import Database, Settings, getch
from pulselogging import PulseLogging
import RPi.GPIO as GPIO

# Global variables
pulseLogging = PulseLogging()
pinInfoDict = {}
keyInfoDict = {}

def setup_pins(simulation):
  if not simulation:
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)

  # Iterate over each meter
  cur = Database.cursor()
  cur.execute("SELECT id, pin, description, bounce_time, pulse_value FROM meters")
  rows = cur.fetchall()

  # Setup callbacks
  def cbGpioCallback(channel):
    pinInfo = pinInfoDict[channel]
    pulseLogging.log_pulse(pinInfo['meter'],1)

  key = '1'
  for rows in rows:
    # Obtain the individual items
    id = rows[0]
    pin = rows[1]
    description = rows[2]
    bounce_time = rows[3]
    pulse_value = rows[4]

    # Save info in the dictionary
    if (not simulation) and (pin >= 0):
      pinInfoDict[pin] = { 'meter': id, 'description': description }

      # Initialize GPIO pins (TODO: Add FALLING/RAISING support)
      GPIO.setup(pin, GPIO.IN)
      GPIO.add_event_detect(pin, GPIO.FALLING, callback=cbGpioCallback, bouncetime = bounce_time)

    # Assign a key to the meter
    keyInfoDict[key] = { 'meter': id, 'description': description }
    key = chr(ord(key) + 1)

    pulseLogging.add_meter(id, description)

def free_pins(simulation):
  if not simulation:
    for pin in pinInfoDict:
      GPIO.remove_event_detect(pin)
    GPIO.cleanup()

# Check if we're running in simulation mode
simulation = Settings.get_bool('server:Simulation')

# Setup all pins
setup_pins(simulation)

# Handle all keystrokes, until 'q' is typed
ch = getch()
while ch != 'q':
  if ch in keyInfoDict:
    keyInfo = keyInfoDict[ch]
    logger.info('Pulse "' + keyInfo['description'] + '" simulated.')
    pulseLogging.log_pulse(keyInfo['meter'],1)
  ch = getch()

# Free the pins
free_pins(simulation)
