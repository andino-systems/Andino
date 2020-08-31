#/bin/bash
printf "Restart SIM800L\n"
#echo "21" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio17/direction
echo "1" > /sys/class/gpio/gpio17/value
echo "0" > /sys/class/gpio/gpio17/value
echo "1" > /sys/class/gpio/gpio17/value
