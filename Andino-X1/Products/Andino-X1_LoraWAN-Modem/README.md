Andino X1 with Raspberry Pi, LoraWAN Modem, Heatsink and RTC
==========

[Andino X1][1] is a base board that allows the raspberry pi to be used in an industrial environment on a DIN Rail. This configuration also includes a LoraWAN modem and the UART RS232-WAN Extension.

**The setup documentation section can be found at the bottom!**

![Andino X1 - Raspberry Pi on DIN Rail](Andino-X1-Raspberry-Pi-in-der-industrie.png)  

### Andino X1
The [Andino X1][1] is a microcontroller board for the Raspberry Pi in a DIN-rail housing for installation in a control cabinet. It is used to adapt digital inputs and outputs for a voltage of 24 V. The X1 has its own microcontroller for precise signal preprocessing and adaptation of signal generators and actuators. It also contains a Raspberry Pi (2/3). The inputs and outputs as well as the power supply of the Pi are optimally protected. Communication between the microcontroller and the Pi takes place via the UART interface.

**For full documentation on the Andino X1 board, see [Andino X1](../../)**

### LoraWAN connectivity
The LoraWAN modem is connected to the UART RS232-WAN extension as descibed in Dual Channel UART RS232-WAN Extension.

### Setup documentation

- [Andino X1: BaseBoard Setup](../../BaseBoard)
- [LoraWAN modem (RN2483): Setup & documentation](../../../Andino-Common/Extensions/LoRaWAN-Modem)

Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)

[1]:https://andino.systems/andino-x1/

