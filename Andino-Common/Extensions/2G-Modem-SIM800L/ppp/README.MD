Setup PPP for the 2G/EDGE SimCom SIM800L or 4G on the SIM7600E Modem
======

*Important: This documentation explains how to install ppp and establish an internet connection using the SimCom SIM800L. If you have not yet established a 2G connection through the modem, please refer to [SimCom SIM800L: Setup (2G/EDGE Modem)](../) first.*

#### Installation

Install ppp before beginning the configuration.

	apt-get install ppp

#### Configuring ppp

"internet.telekom" is my APN and *must* be changed to the providers APN

First we need to create a new file for ppp
    
	sudo nano /etc/ppp/peers/rnet

Enter the following as the file's content. Make sure to change *internet.telekom* in line 2 to the APN of your mobile provider.
 
    #imis/internet is the apn for idea connection
    connect "/usr/sbin/chat -v -f /etc/chatscripts/gprs -T internet.telekom"
    
    # For SIM800 use /dev/ttySC1 as the communication port
    # For SIM7600E use /dev/ttyUSB2 as the communication port
    /dev/ttySC1
    
    # Baudrate
    115200
    
    # Assumes that your IP address is allocated dynamically by the ISP.
    noipdefault
    
    # Try to get the name server addresses from the ISP.
    usepeerdns
    
    # Use this connection as the default route to the internet.
    defaultroute
    
    # Makes PPPD "dial again" when the connection is lost.
    persist
    
    # Do not ask the remote to authenticate.
    noauth
    
    # No hardware flow control on the serial link with GSM Modem
    nocrtscts
    
    # No modem control lines with GSM Modem
    local

Save the file and exit. Now, edit the file

	sudo nano /etc/chatscripts/gprs

Make sure the content of the file is the following:
    
    # You can use this script unmodified to connect to cellular networks.
    # The APN is specified in the peers file as the argument of the -T command
    # line option of chat(8).
    
    # For details about the AT commands involved please consult the relevant
    # standard: 3GPP TS 27.007 - AT command set for User Equipment (UE).
    # (http://www.3gpp.org/ftp/Specs/html-info/27007.htm)
    
    ABORT   BUSY
    ABORT   VOICE
    ABORT   "NO CARRIER"
    ABORT   "NO DIALTONE"
    ABORT   "NO DIAL TONE"
    ABORT   "NO ANSWER"
    ABORT   "DELAYED"
    ABORT   "ERROR"
    
    # cease if the modem is not attached to the network yet
    ABORT   "+CGATT: 0"
    
    ""  AT
    TIMEOUT 12
    OK  ATH
    OK  ATE1
    
    # +CPIN provides the SIM card PIN
    #OK "AT+CPIN=1234"
    
    # +CFUN may allow to configure the handset to limit operations to
    # GPRS/EDGE/UMTS/etc to save power, but the arguments are not standard
    # except for 1 which means "full functionality".
    #OK AT+CFUN=1
    
    OK  AT+CGDCONT=1,"IP","\T","",0,0
    OK  ATD*99#
    TIMEOUT 22
    CONNECT ""

ppp is now configured.


#### Check the connection

First dial by running
    
    sudo pon rnet
    
Check in syslog, if the connection was successful. You should a report of your local and remote ip adress by pppd in the last few lines. You can also check ifconfig to see if the modem connection shows up as an interface.

    tail -n 30 /var/log/syslog
    ifconfig
    
Now add the modem as a default route and try to ping a public IP (e.g. Google DNS)

    sudo route add default dev ppp0
    ping 8.8.8.8
    
If successful, the modem can be disconnected from the internet again

    sudo poff rnet


#### Automatically connect modem after boot

First, open the interface configuration file

	sudo nano /etc/network/interfaces

Make sure the file has the following content (usually three lines before *source-directory* have to be added)

    # interfaces(5) file used by ifup(8) and ifdown(8)
    
    # Please note that this file is written to be used with dhcpcd
    # For static IP, consult /etc/dhcpcd.conf and 'man dhcpcd.conf'
    
    # Include files from /etc/network/interfaces.d:
    
    auto rnet
    iface rnet inet ppp
    provider rnet
      
    source-directory /etc/network/interfaces.d

Save and exit. Then open the rc.local file
    
    sudo nano /etc/rc.local

Directly before the last line (containing *exit 0*), add the following

    printf "Restart SIM800L\n"
    sudo echo "21" > /sys/class/gpio/export
    sudo echo "out" > /sys/class/gpio/gpio21/direction
    sudo echo "1" > /sys/class/gpio/gpio21/value
    sudo echo "0" > /sys/class/gpio/gpio21/value
    sudo echo "1" > /sys/class/gpio/gpio21/value

The modem should now automatically establish an internet connection whenever the pi boots.