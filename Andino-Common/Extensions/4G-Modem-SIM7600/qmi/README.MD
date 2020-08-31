SimCom SIM7600E: Setting up via QMI
======
For a high bandwidth modem like the SIM7600 LTE Modem a connection via USB with the QMI Interface (Qualcomm MSM Interface) is recommended. QMI is supported by the latest version of the Raspbian (Debian Stretch Kernel >= 4.14.98 )

Many thanks to [http://www.embeddedpi.com](http://www.embeddedpi.com) for the great documentation.

1. Install SIM and remove PIN
1. Set the QMI kernel driver to work in raw-ip mode
1. Enable the network interface
1. Connect to the cellular network
1. Run a raw-ip supporting DHCP client to configure the network interface and routing/DNS

### Preparation and install QMI

**Remove PIN from SIM!** for example by using your cell phone ;) 

Open the Housing and insert the Micro SIM.

![Andino Lora - Insert SIM Card](andino-io-sim7600e-inside.png)


Udate to the latest Kernel and apply changes.
 
	sudo -s
	apt-get update
	apt-get upgrade
	reboot

Install QMI Tools

	apt-get install libqmi-utils udhcpc
	reboot

This installs two main utilities (qmi-cli tool and qmi-network helper script) these are used for interaction with the modem (see man qmi-cli for more details)

### Bug Fix and add RAW-IP Support in qmi-network

	sudo nano /usr/bin/qmi-network

Change in Line 337 in start_network ()
from 

	    setup_data_format
		START_NETWORK_ARGS="apn='$APN'"
to

	    echo Y > /sys/class/net/wwan0/qmi/raw_ip
	    setup_data_format
	    START_NETWORK_ARGS="apn='$APN',ip-type=4"

### Configure your APN

 	nano /etc/qmi-network.conf

Add your APN

	APN=internet.eplus.de
	APN_USER=eplus
	APN_PASS=eplus


### Manual steps are..

	ifconfig wwan0 down
	echo Y > /sys/class/net/wwan0/qmi/raw_ip
	ifconfig wwan0 up
	qmi-network /dev/cdc-wdm0 start
	udhcpc -i wwan0

### Automate this by configure /etc/network/interfaces.d/wwan0 

	sudo nano  /etc/network/interfaces.d/wwan0 

Add this:

	iface wwan0 inet manual
	     pre-up ifconfig wwan0 down
	     pre-up echo Y > /sys/class/net/wwan0/qmi/raw_ip
	     pre-up for _ in $(seq 1 10); do /usr/bin/test -c /dev/cdc-wdm0 && break; /bin/sleep 1; done
	     pre-up for _ in $(seq 1 10); do /usr/bin/qmicli -d /dev/cdc-wdm0 --nas-get-signal-strength && break; /bin/sleep 1; done
	     pre-up /usr/bin/qmi-network /dev/cdc-wdm0 start
	     pre-up udhcpc -i wwan0
	     post-down /usr/bin/qmi-network /dev/cdc-wdm0 stop

Now you can start the Network by using this command:


		sudo ifup wwan0

stop with

		sudo ifdown wwan0

Check with 

		rounte -n		
		ping -I wwan0 8.8.8.8 

### Useful commands

	qmicli -d /dev/cdc-wdm0 --nas-get-signal-info
	qmicli -d /dev/cdc-wdm0 --nas-get-signal-strength
	qmicli -d /dev/cdc-wdm0 --nas-get-home-network
	
	qmicli -d /dev/cdc-wdm0 --nas-get-serving-system
	
	qmi-network /dev/cdc-wdm0 status
	qmicli -d /dev/cdc-wdm0  --wds-get-packet-service-status

### References 

[http://www.embeddedpi.com/documentation/3g-4g-modems/raspberry-pi-sierra-wireless-mc7455-modem-raw-ip-qmi-interface-setup](http://www.embeddedpi.com/documentation/3g-4g-modems/raspberry-pi-sierra-wireless-mc7455-modem-raw-ip-qmi-interface-setup)

[https://techship.com/faq/how-to-set-up-a-simple-data-connection-over-qualcomm-qmi-interface-using-libqmi-and-driver-qmi-wwan-in-linux/](https://techship.com/faq/how-to-set-up-a-simple-data-connection-over-qualcomm-qmi-interface-using-libqmi-and-driver-qmi-wwan-in-linux/)



