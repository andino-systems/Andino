from setuptools import find_packages, setup
setup(
    name="andinopy",
    packages=find_packages(include=['andinopy']),
    version='0.1',
    description="Library for Andino.Systems Products",
    author="Jakob Groß - Clear Systems GmbH",
    license='Apache-2.0',
    install_requires=['gpiozero', 'smbus2', 'pyserial', 'adafruit-circuitpython-ssd1306', 'Pillow', 'adafruit-blinka'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests'
)