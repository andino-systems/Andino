#/bin/bash
printf "Start SIM800L\n"
echo "1" > /sys/class/gpio/gpio17/value
