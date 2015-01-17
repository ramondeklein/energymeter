from log import initialize_logging, logging
from config import configuration

# Setup logger
logger = logging.getLogger(__name__)

class Meter:
    def __init__(self, section, callback):
        # Determine the identifier
        self.id = int(section.split(':')[1])

        # Obtain the meter description
        self.description = configuration.get(section, 'description')

        # Create the meter object
        logger.info('Setting up meter %d: %s' % (self.id, self.description))

        # Check if the meter is enabled
        self.enabled = not configuration.has_option('Options', 'myoption') or configuration.getboolean(section, 'enabled')

        # Create the meter object
        if not self.enabled:
            logger.info('- Meter is disabled.')

        # Determine the pulse value
        self.pulse_value = configuration.getfloat(section, 'pulse_value') if configuration.has_option(section, 'pulse_value') else 1.0

        # Determine the unit
        self.unit = configuration.get(section, 'unit')
        self.unit_precision = configuration.getfloat(section, 'unit_precision') if configuration.has_option(section, 'unit_precision') else 1.0

        # Determine the current unit
        self.current_unit = configuration.get(section, "current_unit")
        self.current_factor = configuration.getfloat(section, "current_factor") if configuration.has_option(section, 'current_factor') else 1.0

        # Log the units
        logger.info('- Each pulse is %f%s (current unit shown as "%s")' % (self.pulse_value, self.unit, self.current_unit))

        # Determine the GPIO pin
        self.gpio_pin = configuration.getint(section, "gpio_pin")
        logger.info('- Using GPIO pin %d' % (self.gpio_pin))

        # Determine GPIO pull-up/down
        gpio_pull_mode = configuration.get(section, "gpio_pull_mode") if configuration.get(section, "gpio_pull_mode") else None
        if gpio_pull_mode:
            gpio_pull_mode = gpio_pull_mode.upper()
            if (gpio_pull_mode != 'PULL_UP') and (gpio_pull_mode != 'PULL_DOWN'):
                raise Exception('Invalid value "%s" for option "gpio_pull_mode" in section [%s]' % (gpio_pull_mode, section))
            self.gpio_pull_mode = gpio_pull_mode
            logger.info('- Using GPIO %s mode' % (self.gpio_pull_mode))
        else:
            logger.warn('- No pull-up/down specified (signal might float).')
            self.gpio_pull_mode = None

        # Parse GPIO trigger
        gpio_trigger_edge = configuration.get(section, "gpio_trigger_edge") if configuration.get(section, "gpio_trigger_edge") else 'RAISING'
        gpio_trigger_edge = gpio_trigger_edge.upper()
        if (gpio_trigger_edge != 'RISING') and (gpio_trigger_edge != 'FALLING') and (gpio_trigger_edge != 'BOTH'):
            raise Exception('Invalid value "%s" for option "gpio_trigger_edge" in section [%s]' % (gpio_trigger_edge, section))
        self.gpio_trigger_edge = gpio_trigger_edge
        logger.info('- Using GPIO %s trigger' % (self.gpio_trigger_edge))

        # Determine bounce time
        self.gpio_bounce_time = configuration.getint(section, "gpio_bounce_time") if configuration.get(section, "gpio_bounce_time") else 0
        if self.gpio_bounce_time > 0:
            logger.info('- Input trigger has %dms bounce time' % (self.gpio_bounce_time))
        else:
            logger.info('- Input trigger has no bounce time')

        # Save callback
        self.callback = callback

    def init_gpio(self):
        # Import GPIO
        import RPi.GPIO as GPIO

        # Determine GPIO pull-up/down setting
        pull_mode = None
        if self.gpio_pull_mode:
            if self.gpio_pull_mode == 'PULL_UP':
                pull_mode = GPIO.PUD_UP
            elif self.gpio_pull_mode == 'PULL_DOWN':
                pull_mode = GPIO.PUD_DOWN
            else:
                assert False

        # Determine GPIO edge trigger
        if self.gpio_trigger_edge == 'RISING':
            trigger_edge = GPIO.RISING
        elif self.gpio_trigger_edge == 'FALLING':
            trigger_edge = GPIO.RISING
        elif self.gpio_trigger_edge == 'BOTH':
            trigger_edge = GPIO.RISING
        else:
            assert False

        # Setup the callback
        def gpio_callback(channel):
            assert self.gpio_pin == channel
            self.callback(self)

        # Actually try to configure the input
        try:
            if pull_mode is not None:
                GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=pull_mode)
            else:
                GPIO.setup(self.gpio_pin, GPIO.IN)
            if self.gpio_bounce_time > 0:
                GPIO.add_event_detect(self.gpio_pin, trigger_edge, callback=gpio_callback, bouncetime=self.gpio_bounce_time)
            else:
                GPIO.add_event_detect(self.gpio_pin, trigger_edge, callback=gpio_callback)
        except Exception as exc:
            logger.error('Unable to configure GPIO pin %d (%s): %s' % (self.gpio_pin, self.description, exc.message))
            raise
