#/bin/bash
printf "Dial in\n"
./restart.sh
printf "Sleep a while..\n"
sleep 5
sudo pon rnet
printf "Sleep a while..\n"
sleep 10
sudo route add default dev ppp0
