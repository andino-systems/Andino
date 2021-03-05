#!/bin/bash

printf "#### Andino X1 setup script ####\n"
printf "Starting in:\n"
printf "3..."
sleep 1
printf "2..."
sleep 1
printf "1..."
sleep 1

# update & upgrade
printf "[X1 Setup] Updating & upgrading packages...\n"
sleep 1

printf "\n"
sudo apt-get update
sudo apt-get upgrade -y

# install software
printf "[X1 Setup] Installing software...\n"
sleep 1
sudo apt-get install -y minicom git python python-pip python3 python3-pip
### i2c-tools is installed in RTC section

# edit system files
printf "[X1 Setup] Setting system settings...\n"
sleep 1

## edit /boot/config.txt
printf "Enabling UART in /boot/config.txt..."

echo "" >> /boot/config.txt
sudo echo "enable_uart=1" >> /boot/config.txt
sudo echo "dtoverlay=disable-bt" >> /boot/config.txt
sudo echo "dtoverlay=miniuart-bt" >> /boot/config.txt

printf "done.\n"

## edit /boot/cmdline.txt

printf "Disabling console on /dev/serial0..."

sudo cut -d ' ' -f 3- < /boot/cmdline.txt >> /boot/cmdline-new.txt
sudo rm /boot/cmdline.txt
sudo mv /boot/cmdline-new.txt /boot/cmdline.txt

printf "done.\n"

# configure RTC
printf "[X1 Setup] Setting up RTC...\n"
sleep 1

printf "Enabling rtc in /boot/config.txt..."

sudo echo "" >> /boot/config.txt
sudo echo "dtparam=i2c_arm=on" >> /boot/config.txt
sudo echo "dtoverlay=i2c-rtc,ds3231" >> /boot/config.txt

printf "done.\n"

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

cd /home/pi/
git clone https://github.com/azlux/log2ram.git
chmod +x log2ram/install.sh
sudo ./log2ram/install.sh


# install node.js & node-red

printf "[X1 Setup] Setting up NodeJS & NodeRed...\n"
sleep 1

printf "Starting installation. PLEASE CONFIRM WITH 'y' IF PROMPTED.\n"
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered) --confirm-install --confirm-pi

printf "Enabling Node-Red in systemctl..."
sudo systemctl enable nodered.service
printf "done.\n"

printf "The Node-Red web UI is currently unsecured! For documentation on how to enable username/password authentication, please refer to https://andino.systems/programming/nodered. \n"

printf "Installing custom NodeRed nodes...\n"

cd /home/pi/.node-red/
npm install node-red-contrib-andinox1
npm install node-red-contrib-andino-sms
npm install node-red-contrib-andinooled
cd ~

# install andinopy

printf "[X1 Setup] Setting up Andino Python Library...\n"
sleep 1

## download and unzip
sudo pip3 install wheel
mkdir andinopy
wget 'https://raw.githubusercontent.com/andino-systems/Andino/master/Andino-Common/src/andinopy/andinopy.zip' -O ./andinopy/andinopy.zip
cd andinopy
unzip andinopy.zip
rm andinopy.zip

## setup
sudo python3 setup.py bdist_wheel
sudo pip3 install dist/package.whl

# finish and remove script

printf "[X1 Setup] Setup complete! Please reboot to finish.\n"
rm /home/pi/x1-setup.sh
