#!/usr/bin/python

# Setup logging
import logging
logging.basicConfig(format='%(asctime)s:%(thread)d:%(levelname)s:%(message)s', level=logging.DEBUG)

# Setup logger
logger = logging.getLogger(__name__)

# Initialize GPIO library
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except RuntimeError:
    print("Error importing RPi.GPIO. Make sure you run this script with root privileges.")
    exit(0)

# GPIO settings
GPIO_PIN = 22
GPIO_PULL_UPDOWN = GPIO.PUD_UP
GPIO_DIRECTION = GPIO.BOTH
GPIO_BOUNCE_TIME = 25

def cb_gpio_callback(channel):
    logger.info("#{}:{}.".format(str(channel), str(GPIO.input(channel))))

# Setup the input
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO_PULL_UPDOWN)
if GPIO_BOUNCE_TIME > 0:
    GPIO.add_event_detect(GPIO_PIN, GPIO_DIRECTION, callback=cb_gpio_callback, bouncetime=GPIO_BOUNCE_TIME)
else:
    GPIO.add_event_detect(GPIO_PIN, GPIO_DIRECTION, callback=cb_gpio_callback)

import time
while True:
    time.sleep(1000);
