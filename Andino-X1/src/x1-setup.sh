#!/bin/sh

echo -n "Andino X1 setup script"


# update & upgrade
echo -n "[X1 Setup] Updating & upgrading packages..."
sleep 1

echo -n ""
sudo apt-get update
sudo apt-get upgrade -y

# install software
echo -n "[X1 Setup] Installing software..."
sleep 1
sudo apt-get install -y minicom git python python-pip python3 python3-pip
### i2c-tools is installed in RTC section

# edit system files
echo -n "[X1 Setup] Setting system settings..."
sleep 1

## edit /boot/config.txt
echo -n "Enabling UART in /boot/config.txt..."

echo "" >> /boot/config.txt
echo "enable_uart=1" >> /boot/config.txt
echo "dtoverlay=disable-bt" >> /boot/config.txt
echo "dtoverlay=miniuart-bt" >> /boot/config.txt

echo "done."

## edit /boot/cmdline.txt

echo -n "Disabling console on /dev/serial0..."

sudo cut -d ' ' -f 3- < /boot/cmdline.txt >> /boot/cmdline-new.txt
sudo rm /boot/cmdline.txt
sudo mv /boot/cmdline-new.txt /boot/cmdline.txt

echo "done."

# configure RTC
echo -n "[X1 Setup] Setting up RTC..."
sleep 1

echo -n "Enabling rtc in /boot/config.txt..."

sudo echo "" >> /boot/config.txt
sudo echo "dtparam=i2c_arm=on" >> /boot/config.txt
sudo echo "dtoverlay=i2c-rtc,ds3231" >> /boot/config.txt

echo "done."

echo -n "Installing necessary packages..."
sudo apt-get install -y i2c-tools
sudo apt-get purge -y fake-hwclock
sudo apt-get remove fake-hwclock -y 

echo -n "Finishing RTC setup..."
sudo dpkg --purge fake-hwclock 
sudo rm -f /etc/adjtime.
sudo cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime
sudo ln -s /home/pi/bin/ntp2hwclock.sh /etc/cron.hourly/ntp2hwclock

echo -n "Downloading NTP script..."
mkdir /home/pi/bin/
wget 'https://raw.githubusercontent.com/andino-systems/Andino/master/Andino-Common/src/rtc/ntp2hwclock.sh' -O /home/pi/bin/ntp2hwclock.sh

# install log2ram

echo -n "[X1 Setup] Setting up Log2Ram..."
sleep 1

cd /home/pi/
git clone https://github.com/azlux/log2ram.git
chmod +x log2ram/install.sh
sudo ./log2ram/install.sh


# install node.js & node-red

echo -n "[X1 Setup] Setting up NodeJS & NodeRed..."
sleep 1

echo -n "Starting installation. PLEASE CONFIRM WITH 'y' IF PROMPTED. "
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered) --confirm-install --confirm-pi

echo -n "Enabling Node-Red in systemctl..."
sudo systemctl enable nodered.service
echo "done"

echo -n "The Node-Red web UI is currently unsecured! For documentation on how to enable username/password authentication, please refer to https://andino.systems/programming/nodered"

echo -n "Installing custom NodeRed nodes..."

cd /home/pi/.node-red/
npm install node-red-contrib-andinox1
npm install node-red-contrib-andino-sms
npm install node-red-contrib-andinooled
cd ~

# install andinopy

echo -n "[X1 Setup] Setting up Andino Python Library..."
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

echo -n "[X1 Setup] Setup complete! Please reboot to finish."
rm /home/pi/x1-setup.sh
