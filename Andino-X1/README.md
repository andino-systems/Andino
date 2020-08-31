Andino X1
==========

**This page provides a general introduction on the Andino X1. For documentation and setup tutorials about a specific product, please choose an entry from this list:**

- **[Andino X1 with Raspberry Pi, Breadboard, Heatsink and RTC](./Products/Andino-X1_Breadboard)**
- **[Andino X1 with Raspberry Pi, isolated RS485/RS422, Heatsink and RTC](./Products/Andino-X1_RS485-RS422)**
- **[Andino X1 with Raspberry Pi, dual Channel RS232, Heatsink and RTC](./Products/Andino-X1_Dual-RS232)**
- **[Andino X1 with Raspberry Pi, 7 digital Inputs, Heatsink and RTC](./Products/Andino-X1_7-Inputs)**
- **[Andino X1 with Raspberry Pi, 2DO/1DI, Heatsink and RTC](./Products/Andino-X1_2DO-1DI)**
- **[Andino X1 with Raspberry Pi, CAN Bus, Heatsink and RTC](./Products/Andino-X1_CAN-Bus)**
- **[Andino X1 with Raspberry Pi, LoraWAN, Heatsink and RTC](./Products/Andino-X1_LoraWAN)**
- **[Andino X1 with Raspberry Pi, 2G Modem, Heatsink and RTC](./Products/Andino-X1_2G-Modem)**
- **[Andino X1 with Raspberry Pi, 4G Modem, Heatsink and RTC](./Products/Andino-X1_4G-Modem)**

**For more technical documentation on the base board, including setup tutorials and download links for drivers and firmware, please refer to [Andino X1: BaseBoard Setup](./BaseBoard)**

![Andino X1 - Raspberry Pi on DIN Rail](Andino-X1-Raspberry-Pi-in-der-industrie.png)  

[Andino X1][1] is a base board that allows the raspberry pi to be used in an industrial environment on a DIN Rail.

## Overview

The [Andino X1][1] is a microcontroller board for the Raspberry Pi in a DIN-rail housing for installation in a control cabinet. It is used to adapt digital inputs and outputs for a voltage of 24 V. The X1 has its own microcontroller for precise signal preprocessing and adaptation of signal generators and actuators. It also contains a Raspberry Pi (2/3). The inputs and outputs as well as the power supply of the Pi are optimally protected. Communication between the microcontroller and the Pi takes place via the UART interface.

The [Andino X1][1] offers the following advantages:

The sensitive GPIO of the Raspberry Pi are protected. Fast signals can be precisely detected by the microcontroller. Actuators and sensors can be electrically connected to the Raspberry Pi. It provides an industrial power supply for the Raspberry Pi. Customized adapters from the Raspberry Pi GPIO or the micro controller IO can be connected electrically to terminals. Provides mounting on a DIN rail for installation in manifolds.

#### Raspberry Pi compatible 
The 40-pin connector is compatible with Raspberry Pi 3 B and Raspberry Pi 4

#### Arduino compatible 
The Atmel microcontroller of the Andino X1 comes with an Arduino-compatible bootloader. The combination of Arduino and Raspberry Pi on the Andino X1 is ideally suited for use in home automation and sensor technology, as well as in more demanding industrial automation applications. The strengths of both boards complement each other perfectly. While the single-board computer Raspberry Pi can perform complex tasks (eg hosting of database and WebServer) as a full-value computer, the Arduino microcontroller can take care of the fast signal pre-processing. The Atmel Controller communicates via UART with the Pi. Programmable is the X1 with the Arduino IDE via USB from a PC or from a Raspberry (firmware update in the field).

#### Integrated power supply 
The X1 board has a 9-24V wide-range DC input with reverse polarity protection. Powerful, reliable, stable power supply: 5 Volt, 2.6 Amp – enough power for the Raspberry, your USB hardware and customer-specific adaptation. The integrated EMC protection circuits protect the Pi from voltage surges and current surges on the supply line.

#### 8 Bit Microcontroller 
Programmable 8-bit microcontroller (Atmega 168 8Mhz) for adapting the inputs and outputs. Accurate and reliable detection of digital and analog signals.

#### Galvanically isolated 
The X1 board has two electrically isolated inputs (up to 5kV isolated) as well as two relay outputs for 42 volts and 1 amp. The IO is controlled by a microcontroller. Further GPIO of the Raspberry Pi as well as IO of the Microcontroller are led on an internal pin header. This makes it possible to bring own adaptations to the screw terminals.

#### Expandable
Via the SPI and the I2C interface of the Raspberry Pi, further hardware extensions can be connected and led to the free screw terminals. 

<img src="./img/Extension-Pinout.png" width="300" height="293">

#### Realtime Clock (RTC)
The integrated, battery-buffered RTC provides the correct time even if no NTP (time) server is available. The high-precision time chip DS3231 from Dallas Semiconductors is used. Due to the internal temperature compensation of the oscillator, the chip achieves a very high accuracy of ± 2ppm at 0 ° C to + 40 ° C.

## Block diagram
![Andino X1 - Raspberry Pi on DIN Rail - Block diagram](./img/Andino-X1-Block-schema-1024x671.png)

### Application examples
* Data collection on production machines
* Collect and count Number of items, products
* Downtime detection
* Create Performance indicators Creation such as OEE, GAE and utilization
* Data collection at environmental monitoring stations
* Telecontrol and protocol converters
* Central in the house automation
* IoT nodes

### Programming examples

**[How to use Andino X1 with Node red](./src/node-red-contrib-andinox1)**   
**[How to use Andino X1 with python](./src/python)**   
**[Example Firmware](./src/firmware)**   


Author
-----

* 2020 by [AndinoSystems][2]
* [Contact us by email](mailto:info@andino.systems)

[1]:https://andino.systems/andino-x1/
[2]:https://github.com/andino-systems/Andino-X1

