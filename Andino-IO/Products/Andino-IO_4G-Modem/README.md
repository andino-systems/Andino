Andino IO with Raspberry Pi, 4G Modem, Heatsink and RTC
======

The [Andino IO][1] is a motherboard for the Raspberry Pi. It allows mounting on a DIN rail in the control cabinet.

**The setup documentation section can be found at the bottom!**

![Andino IO - Raspberry Pi on DIN Rail](andino-io-4g-modem.png)  

### Andino IO
The [Andino IO][1] is a microcontroller board for the Raspberry Pi in a DIN-rail housing for installation in a control cabinet. It is used to adapt digital inputs and outputs for a voltage of 24 V. It also contains a Raspberry Pi. The inputs and outputs as well as the power supply of the Pi are optimally protected. Communication between the microcontroller and the Pi takes place via the UART interface.

**For a general introduction on the Andino IO board, see [Andino IO](../../)**

### 4G Connectivity
The 4G modem is connected via USB. Using an LTE connection it can be used for high speed data transmission at a speed of up to 300 Mbit/s. It can also be used to send and receive SMS messages.

### Setup documentation

- [Andino IO: BaseBoard Setup](../../BaseBoard)
- [How to set up the 4G modem via qmi](../../../Andino-Common/Extensions/4G-Modem-SIM7600/qmi)
- [How to set up the 4G modem via ppp (not recommended for data transfer)](../../../Andino-Common/Extensions/4G-Modem-SIM7600/ppp)
- [How to send / receive SMS](../../../Andino-Common/Extensions/4G-Modem-SIM7600/sms)

### Programming examples

- [Using NodeRed with the Andino X1](../../../Andino-Common/src/NodeRed) 
- [Using NodeRed to send and receive SMS](../../../Andino-Common/src/NodeRed/AndinoSMS/node-red-contrib-andino-sms) 

Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)

[1]:https://andino.systems/andino-io/

