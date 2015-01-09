# energymeter
Energy meter for the Raspberry Pi

## Schema
You can use the following schema and connect it to the Raspberry Pi (credits to Diederich Kroeske). Make sure you
use 3.3V VDC. Using 5V will damage your GPIO inputs. This schema can be used for an Arduino board as well and then
you have to use the 5V VDC. Make sure you change R2 accordingly to compensate for the higher voltage.

![Schema](images/schema.png)

The schema shows a BPX81, but we have used a BPW40 instead. The LEDs are useful for debugging. Note that in this 
schema the LEDs are ON and go OFF when a pulse is detected. If you want it the other way around, then connect the 
LED to ground (reverse LED as well to keep the current flowing).

Resistor capacities:

* R1: 10kOhm - 150kOhm (use higher resistance for higher sensitivity)
* R2: 270Ohm (use lower for brighter LED)