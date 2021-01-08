# Standard Andino X1 Firmware

This is the default firmware for the Andino X1. **For full documentation, visit [andino.systems](https://andino.systems/andino-x1/firmware/counting)**

## Changelog

### Version 007 (210107)

* Inputs that are used for temperature sensors will no longer be printed out in the periodic input messages when HARD 4 is selected.
* Fixed issue where the Temperature sensors would not be displayed correctly immediately after startup
* Temporarily disabled RESET command since a bug in the Arduino bootloader caused the board to enter a reboot loop. The command will be re-enabled in a future firmware version.


### Version 006 (201223)

* Added support for the DS18B20 temperature sensor on two busses
* Fixed an issue which caused the controller not to come back online after performing the RESET command on certain hardware configurations

### Version 005 (201106)

* Added support for relay status display in the periodic update messages

## Interface, Commands

All commands or messages are sent and received via  /dev/ttyS0.
Every command has to be terminated by CR or LF. Message ends with CR and LF.
### Commands to the Controller
**Command** | Arguments | Action | Example 
--- | --- | --- | ---
RESET | none | Restart the Controller (disabled since version 210107) | RESET
INFO | none| Prints the current settings | INFO
HARD | 0=noShield, 1=1DI2DO, 2=3DI, 3=5DI, 4=DS18B20 | Set the Hardware configuration | 0 - none
POLL | Cycle in ms | Sets the sampling cycle of the digital inputs [in ms] | POLL 1000
SKIP | Number of polls | Skip n Scans after pulse reconized | 0
EDGE | HL(0) LH(1) | Count on edge HL or LH | EDGE
SEND | Cycle in ms | The counter will send all nnn milliseconds | SEND 5000
SENDT | Cycle in ms | The counter will poll and send the busses every nnnn milliseconds | SENDT 8000
CHNG | Send on Change | Send if any Pin changes. Carefull if many changes | CHNG 1
CNTR | Send Counter | Send counter+states(1) or only states(0) (default 1) | CNTR 0
DEBO | Number of polls | Sets the debounce count. The signal has to be stable for nn polls | DEBO 100
POWR | state (0 or 1)| Power-Out Relay is switched on or off | REL1 1
REL? | on-off  (0 or 1)| Send the current state of the Relays
REL1 | state (0 or 1)| Relay 1 is switched on or off | REL1 1
REL2 | state (0 or 1)| Relay 2 is switched on or off | REL2 1
REL3 | state (0 or 1)| Relay 3 is switched on or off | REL3 1
REL4 | state (0 or 1)| Relay 4 is switched on or off | REL4 1
RPU1 | pulse in sec | Pulse the Relay 1 for nns seconds | RPU1 2
RPU2 | pulse in sec | Pulse the Relay 2 for nns seconds | RPU2 2
TBUS | 1=one bus, 2=2 busses | Sets the number of temperature sensor busses to 1 or 2 | TBUS 2
ADDRT | 1=bus1, 2=bus2 | displays the addresses of all sensors connected to the specified bus | ADDRT 1

Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)
