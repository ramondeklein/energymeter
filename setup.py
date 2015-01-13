from distutils.core import setup

setup(
    name='EnergyMeter',
    description='Energy Metering for Raspberry Pi',
    version='0.1',
    url='https://github.com/ramondeklein/energymeter',
    license='GNU General Public License v2',
    author='Ramon de Klein',
    author_email='mail@ramondeklein.nl',
    packages=['emhelpers'],
    requires=['Flask','dateutil']
)
