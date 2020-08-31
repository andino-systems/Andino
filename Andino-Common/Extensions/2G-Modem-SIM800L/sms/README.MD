SimCom SIM800L: Sending and receiving SMS
======

*Important: This documentation explains how to send and receive messages through the SimCom SIM800L modem using minicom. However, the shown commands can also be used in other environments.*

*If you have not yet established a 2G connection through the modem, please refer to [SimCom SIM800L: Setup (2G/EDGE Modem)](../) first.*

####Configuration
If not already done, run minicom on the pi.

Although it is also possible to send SMS in PDU mode, it is recommended to set the modem to text mode as this makes the operation significantly simpler.

	#Change mode. 0 for PDU mode / 1 for text mode
	AT+CMGF=1

####Sending SMS
SMS can be sent using the *at+cmgs=* command, followed by the recipient phone number in quotation marks. After sending the command, a message can be entered. To send the message, press *Ctrl+Z*.

	at+cmgs="+491575123456"
	> Testing message, let's hope this works... [Ctrl+Z]
	+CMGS: 1

####Reading Received SMS
To print out received unread SMS, run

	at+cmgl="REC UNREAD"
	+CMGL: 3,"REC UNREAD","+491575123456","","20/08/03,15:08:46+08"
	Your message arrived perfectly fine!

The sender phone number, date and time will be printed out followed by the message in the next line. Note that "read" SMS messages will not show up here as they are not saved. To keep SMS messages permanently they can be moved to SMS storage. For details and more commands, refer to the [SIM800 Series_AT Command Manual_V1.09](https://cdn-shop.adafruit.com/product-files/2637/SIM800+Series_AT+Command+Manual_V1.09.pdf) by SIM Tech.
	

