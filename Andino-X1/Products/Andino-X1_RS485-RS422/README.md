Industrial PC Andino X1 with Raspberry Pi, isolated RS485/RS422, Heatsink and RTC
==========

[Andino X1][1] is a base board that allows the raspberry pi to be used in an industrial environment on a DIN Rail. This configuration also includes an extension providing dual channel RS232.

**The setup documentation section can be found at the bottom!**

![Andino X1 - Raspberry Pi on DIN Rail](./img/Andino-X1-Raspberry-Pi-in-der-industrie.png)  

### Andino X1
The [Andino X1][1] is a microcontroller board for the Raspberry Pi in a DIN-rail housing for installation in a control cabinet. It is used to adapt digital inputs and outputs for a voltage of 24 V. The X1 has its own microcontroller for precise signal preprocessing and adaptation of signal generators and actuators. It also contains a Raspberry Pi. The inputs and outputs as well as the power supply of the Pi are optimally protected. Communication between the microcontroller and the Pi takes place via the UART interface.

**For an introduction on the Andino X1 board, see [Andino X1](../../)**

### RS485 and RS422 Extension
This Plugin for the [Andino X1][1], provides a single channel, fully Isolated RS485 extension for the Raspberry Pi or the Arduino Controller. This PlugIn can be jumpered as a two wire, half duplex or as a four wire full duplex interface. This Board based on the SPI Uart from NXP [SC16IS752][3]. The SPI Channel can be jumpered to the Raspberry Pi or the Arduino Controller. With the Arduino Controller time critical protocols can be implemented or a general pre processing of the data can be performed. For setup tutorials and full documentation refer to the setup section below

### Setup documentation

- [Andino X1: BaseBoard Setup](../../BaseBoard)
- [Fully isolated RS485 and RS422 Extension: Setup](../../../Andino-Common/Extensions/RS485_RS422)

### Programming examples

- [Using NodeRed with the Andino X1](../../../Andino-Common/src/NodeRed) 


Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)

[1]:https://andino.systems/andino-x1/

