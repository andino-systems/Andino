#!/bin/bash

printf "#### Andino X1 setup script ####\n"
printf "!This script needs to be executed as user pi! You are currently: "
whoami
printf "\nStarting installation in:\n"
printf "5..."
sleep 1
printf "4..."
sleep 1
printf "3..."
sleep 1
printf "2..."
sleep 1
printf "1...\n"
sleep 1

cd /home/pi || exit 2
mkdir tmp

# update & upgrade
printf "[X1 Setup] Updating & upgrading packages...\n"
sleep 1

sudo apt-get update
sudo apt-get upgrade -y

# install software
printf "[X1 Setup] Installing software...\n"
sleep 1
sudo apt-get install -y minicom screen elinks git python python-pip python3 python3-pip
### i2c-tools is installed in RTC section

# edit system files
printf "[X1 Setup] Setting system settings...\n"
sleep 1

## edit /boot/config.txt
printf "Enabling UART in /boot/config.txt...\n"

echo "" | sudo tee -a /boot/config.txt
echo "enable_uart=1" | sudo tee -a /boot/config.txt
echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt
echo "dtoverlay=miniuart-bt" | sudo tee -a /boot/config.txt


printf "...done\n"

## edit /boot/cmdline.txt

printf "Disabling console on /dev/serial0...\n"

cut -d ' ' -f 3- < /boot/cmdline.txt | sudo tee /boot/cmdline.txt

printf "...done.\n"

# configure RTC
printf "[X1 Setup] Setting up RTC...\n"
sleep 1

printf "Enabling rtc in /boot/config.txt...\n"

echo "" | sudo tee -a /boot/config.txt
echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
echo "dtoverlay=i2c-rtc,ds3231" | sudo tee -a /boot/config.txt

printf "...done.\n"

printf "Installing necessary packages...\n"
sudo apt-get install -y i2c-tools
sudo apt-get purge -y fake-hwclock
sudo apt-get remove fake-hwclock -y 

printf "Finishing RTC setup...\n"
sudo dpkg --purge fake-hwclock 
sudo rm -f /etc/adjtime.
sudo cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime
sudo ln -s /home/pi/bin/ntp2hwclock.sh /etc/cron.hourly/ntp2hwclock

printf "Downloading NTP script...\n"
mkdir /home/pi/bin/
wget 'https://raw.githubusercontent.com/andino-systems/Andino/master/Andino-Common/src/rtc/ntp2hwclock.sh' -O /home/pi/bin/ntp2hwclock.sh

# install log2ram

printf "[X1 Setup] Setting up Log2Ram...\n"
sleep 1

cd /home/pi/ || exit 2
git clone https://github.com/azlux/log2ram.git
chmod +x log2ram/install.sh
sudo ./log2ram/install.sh

# install node.js & node-red

printf "[X1 Setup] Setting up NodeJS & NodeRed...\n"
sleep 1

printf "Starting installation. PLEASE CONFIRM WITH 'y' IF PROMPTED.\n"
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered) --confirm-install --confirm-pi

printf "Enabling Node-Red in systemctl...\n"
sudo systemctl enable nodered.service
printf "...done.\n"

printf "The Node-Red web UI is currently unsecured! For documentation on how to enable username/password authentication, please refer to https://andino.systems/programming/nodered. \n"

printf "Installing custom NodeRed nodes...\n"

cd /home/pi/.node-red/ || exit 2
npm install node-red-contrib-andinox1
npm install node-red-contrib-andino-sms
npm install node-red-contrib-andinooled
cd ~ || exit 2

printf "...done.\n"

# RS232

printf "Setting up RS232...\n"

echo "" | sudo tee -a /boot/config.txt
echo "dtoverlay=spi0-2cs,cs0_pin=8,cs1_pin=12,cs0_spidev=off,cs_1_spidev=off" | sudo tee -a /boot/config.txt
echo "dtoverlay=sc16is752-spi0,int_pin=7,xtal=11059200" | sudo tee -a /boot/config.txt

printf "...done.\n"

# install andinopy

printf "[X1 Setup] Setting up Andino Python Library...\n"
sleep 1

## download and unzip
sudo pip3 install wheel
mkdir andinopy
wget 'https://raw.githubusercontent.com/andino-systems/Andino/master/Andino-Common/src/andinopy/andinopy.zip' -O ./andinopy/andinopy.zip
cd andinopy || exit 2
unzip andinopy.zip
rm andinopy.zip

## setup
sudo python3 setup.py bdist_wheel
sudo pip3 install dist/andinopy-0.1-py3-none-any.whl

# finish and remove script

printf "[X1 Setup] Setup complete! Please reboot to finish.\n"
rmdir /home/pi/tmp
rm /home/pi/x1-setup.sh
