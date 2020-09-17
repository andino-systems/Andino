Andino: SMS Handling Nodes
====================

A collection of [Node-RED][1] nodes that enable sending and receiving SMS from [Andino](../../../../../) boards.

-------

# Node documentation

This package contains 4 nodes enabling different aspects of SMS handling using the Raspberry Pi and a 2G/4G modem on the Andino. The following sections explain the functionality of each node. The nodes use at commands to communicate with the modem in conjunction with serial nodes.

## SMS Sender

This Node, in conjunction with a serial out node, enables sending SMS to a target phone number. 

*The node requires two input values:*

* **msg.number** (String) - The phone number of the intended recipient. It is recommended, but not always necessary, to include the country code in phone numbers. The number has to be in a dialable format. (eg. +4915123456)
* **msg.payload** (String) - The message that will be sent to the recipient.

The node then sends three output messages (switching the modem to text mode, entering the phone number, entering the message).

## SMS Checker

The SMS Checker node sends out a request reading all unread messages to the modem when receiving an input. It first sets to modem to text mode, then sends a check SMS command.

## SMS Listener

This node checks all inputs for an indicator message, that a new SMS has arrived (*+CMTI:*). When receiving a matching message, it relays the message to the next node.

The SMS Listener node can be used in conjunction with the SMS Checker node to automatically check for incoming messages. (see example flows below)

## SMS Processor

The SMS Processor node takes incoming signals messages from a serial node, checks if the input is part of an SMS message and returns a message with the following variables:

* **msg.payload** (String) - The content of the SMS.
* **msg.number** (String) - The number the SMS has been sent from.
* **msg.timestamp** (String) - The arrival time of the SMS.

# Example Flows



Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)

[1]:https://nodered.org
[2]:https://andino.systems/andino-x1/
