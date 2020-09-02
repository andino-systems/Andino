Andino X1 with Raspberry Pi, 7 digital Inputs, Heatsink and RTC
======

[Andino X1][1] is a base board that allows the raspberry pi to be used in an industrial environment on a DIN Rail. This configuration also includes a 5 digital inputs extension. Combined with the two VCC inputs, the total amount of digital inputs on this Andino X1 configuration is seven.

**The setup documentation section can be found at the bottom!**

![Andino X1 - Raspberry Pi on DIN Rail](./img/Andino-X1-Raspberry-Pi-in-der-industrie.png)  

### Andino X1
The [Andino X1][1] is a microcontroller board for the Raspberry Pi in a DIN-rail housing for installation in a control cabinet. It is used to adapt digital inputs and outputs for a voltage of 24 V. The X1 has its own microcontroller for precise signal preprocessing and adaptation of signal generators and actuators. It also contains a Raspberry Pi. The inputs and outputs as well as the power supply of the Pi are optimally protected. Communication between the microcontroller and the Pi takes place via the UART interface.

**For an introduction on the Andino X1 board, see [Andino X1](../../)**

### 5 digital inputs extension

The addition of the 5 digital inputs extension increases the total number of inputs on the Andino X1 to seven. The extension board is connected using the extension pin header.

 ![Andino X1 - 7 Inputs schematics](./img/Andino-X1-schematic-structure.png) 


### Setup documentation

- [Andino X1: BaseBoard Setup](../../BaseBoard)
- [5 Digital Inputs extension: Setup](../../../Andino-Common/Extensions/5DI)

### Programming examples

- [Using NodeRed with the Andino X1](../../../Andino-Common/src/NodeRed) 

Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)

[1]:https://andino.systems/andino-x1/

