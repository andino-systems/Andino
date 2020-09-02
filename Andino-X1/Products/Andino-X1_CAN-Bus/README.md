Andino X1 with Raspberry Pi, CAN Bus, Heatsink and RTC
==========

[Andino X1][1] is a base board that allows the raspberry pi to be used in an industrial environment on a DIN Rail. This configuration also includes a CAN Bus interface.
![Andino X1 - Raspberry Pi on DIN Rail](./img/Andino-X1-Raspberry-Pi-in-der-industrie.png)  

**The setup documentation section can be found at the bottom!**

### Andino X1
The [Andino X1][1] is a microcontroller board for the Raspberry Pi in a DIN-rail housing for installation in a control cabinet. It is used to adapt digital inputs and outputs for a voltage of 24 V. The X1 has its own microcontroller for precise signal preprocessing and adaptation of signal generators and actuators. It also contains a Raspberry Pi. The inputs and outputs as well as the power supply of the Pi are optimally protected. Communication between the microcontroller and the Pi takes place via the UART interface.

**For an introduction on the Andino X1 board, see [Andino X1](../../)**

### CAN Bus interface

The CAN Bus extension allows controlling devices via the BUS interface using the Andino X1 / Raspberry Pi. For full documentation on connectivity and schematics refer to the setup documentation section below. 

### Setup documentation

- [Andino X1: BaseBoard Setup](../../BaseBoard)
- [CAN Bus Extension: Setup](../../../Andino-Common/Extensions/CAN)

### Programming examples

- [Using NodeRed with the Andino X1](../../../Andino-Common/src/NodeRed) 


Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)

[1]:https://andino.systems/andino-x1/

