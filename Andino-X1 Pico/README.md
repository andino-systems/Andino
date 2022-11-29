# Standard Andino X1 Pico Firmware

This is the default firmware for the Andino X1 Pico. **For full documentation, visit [andino.systems](https://andino.systems/andino-x1/firmware/counting)**

## Changelog

### Version 008 (210114)

**This version introduces compatibility with the common andino protocol. Make sure to update other software communicating with this firmware if you use the temperature sensor bus functionality!**
* increased minimum Send Cycle of temperature messages to 2000 ms to make unresponsive behavior less likely
* added POLLT command
* added support for new common andino protocol
* combined message counter for temperature and input/relay status messages

Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)
