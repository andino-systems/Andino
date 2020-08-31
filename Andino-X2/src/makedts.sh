#/bash
dtc -@ -I dts -O dtb -o sc16is752-spi0-ce1.dtbo sc16is752-spi0-ce1.dts
cp ./sc16is752-spi0-ce1.dtbo /boot/overlays/
