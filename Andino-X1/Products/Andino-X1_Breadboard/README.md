Industrial PC with Raspberry Pi, Breadboard, Heatsink and RTC
==========

[Andino X1][1] is a base board that allows the raspberry pi to be used in an industrial environment on a DIN Rail. This configuration also comes pre-installed with a breadboard.

![Andino X1 - Raspberry Pi on DIN Rail](Andino-X1-Raspberry-Pi-in-der-industrie.png)  

### Andino X1
The [Andino X1][1] is a microcontroller board for the Raspberry Pi in a DIN-rail housing for installation in a control cabinet. It is used to adapt digital inputs and outputs for a voltage of 24 V. The X1 has its own microcontroller for precise signal preprocessing and adaptation of signal generators and actuators. It also contains a Raspberry Pi. The inputs and outputs as well as the power supply of the Pi are optimally protected. Communication between the microcontroller and the Pi takes place via the UART interface.

**For an introduction on the Andino X1 board, see [Andino X1](../../)**

### Breadboard
The breadboard that comes pre-installed with the Andino X1 enables easy prototyping for additional projects and extensions. It provides easy access to the all pins of the pin header and thus the I2C and SPI busses. The layout of the breadboard is as follows:

<img src="./breadboard-extension-small.png" width="414" height="320">

Overview over all PIN mappings of the Extension PIN header:

<img src="./Extension-Pinout.png" width="414" height="320">

### Setup documentation

- [Andino X1: BaseBoard Setup](../../BaseBoard)

### Programming examples

- [Using NodeRed with the Andino X1](../../../Andino-Common/src/NodeRed)


Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)

[1]:https://andino.systems/andino-x1/

