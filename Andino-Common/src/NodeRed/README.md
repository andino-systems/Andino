Installing Node-Red on the Raspberry Pi
====================

* **This tutorials details how to install Node-Red on the Raspberry Pi for Andino Boards.**
* **For documentation on all custom Andino nodes, refer to section 3 at the bottom of the page.**

-------

# How to Install

## 1) Installing Log2Ram
To save write cycles on your SD Card you can install [Log2Ram](https://github.com/azlux/log2ram) which stores the Log Files in memory. This isn't strictly necessary but highly recommended as it dramatically increases the lifespan of the Pi SD card.

First, install git:

	sudo apt -y install git

Get log2ram from the git repository:

	git clone https://github.com/azlux/log2ram.git

Enter the new directory and make the install script executable, then run the script:

	cd log2ram
	chmod +x install.sh
	sudo ./install.sh

Finally, reboot the Pi:

	sudo reboot now 

Check if log2ram is running. The command

	df -h

should reveal it as an entry:

	log2ram          40M  452K   40M   2% /var/log


## 2) Installing Node.js and Node-Red


After that you can install Node.js and Node-Red. 

	bash <(curl -sL https://raw.githubusercontent.com/node-red/raspbian-deb-package/master/resources/update-nodejs-and-nodered) 

To run Node Red from the terminal

	node-red-pi

To run Nore-Red in background on boot:

	sudo systemctl enable nodered.service

Node-Red is now fully set up and can be reached on port *1880* by default.


## 3.) Installing custom Nodes

While this configuration already offers some functionality, there are several purpose-built nodes for usage on Andino boards. A full list of all available nodes can be viewed by going to the Node-Red Settings, selecting *Palette* and *Install*. Here, search for *andino* to see a list of all Nodes.

**All nodes can be installed in two ways:**

*  Search for the package name of the node/node collection in the Palette manager (see section above)


*  Install the node with npm:
	
	 sudo npm install packageName 


The following Nodes are available for Andino boards:

### Andino X1 Node

**Package name:** *node-red-contrib-andinox1*

This Node enables communication between the Raspberry Pi and the Arduino controller on the Andino X1 board. What this Node does specifically is:

1.) Convert the Serial Message from the Arduino Controller to an Payload Object so that you can access payload.Counter1 for instance.

2.) Convert a Boolean to a Relay-Message for the Microcontroller (see the Example)   

For detailed documentation on the node, refer to [Andino X1 Node](./AndinoX1Node/node-red-contrib-andinox1).

### Andino SMS Node collection

This collection includes four nodes that facilitate sending and receiving SMS messages on an Andino board using a 2G or 4G modem. 

For setup instructions refer to [Andino SMS Nodes](./AndinoSMS/node-red-contrib-andino-sms)


----
Some more information and samples about Node Red

https://randomnerdtutorials.com/getting-started-with-node-red-on-raspberry-pi/

Author
-----

* 2020 by AndinoSystems
* [Contact us by email](mailto:info@andino.systems)

[1]:https://nodered.org
[2]:https://andino.systems/andino-x1/
