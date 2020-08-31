#/bin/bash
printf "Stop SIM800L\n"
echo "0" > /sys/class/gpio/gpio17/value
