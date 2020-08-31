Andino X1 with Raspberry Pi, 2DO/1DI, heat sink and RTC
======

[Andino X1][1] is a base board that allows the raspberry pi to be used in an industrial environment on a DIN Rail. This configuration also includes an extension providing two additional digital outputs and one additional digital input.

**The setup documentation section can be found at the bottom!**

![Andino X1 - Raspberry Pi on DIN Rail](./img/Andino-X1-Raspberry-Pi-in-der-industrie.png)  

### Andino X1
The [Andino X1][1] is a microcontroller board for the Raspberry Pi in a DIN-rail housing for installation in a control cabinet. It is used to adapt digital inputs and outputs for a voltage of 24 V. The X1 has its own microcontroller for precise signal preprocessing and adaptation of signal generators and actuators. It also contains a Raspberry Pi. The inputs and outputs as well as the power supply of the Pi are optimally protected. Communication between the microcontroller and the Pi takes place via the UART interface.

**For an introduction on the Andino X1 board, see [Andino X1](../../)**

### 2DO/1DI Extension
With this extension adding two relays and one digital input to the Andino X1, the system has a total of three inputs and 4 relays. The Inputs are galvanically isolated up to 5kV. For full documentation and connectivity of the extension, please refer to the setup section below.

### Setup documentation

- [Andino X1: BaseBoard Setup](../../BaseBoard)
- [2 Digital Output / 1 Digital Input Extension: Setup](../../../Andino-Common/Extensions/2DO1DI)

Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)

[1]:https://andino.systems/andino-x1/

