# I2C OLED System Ressource monitor, by Christian Drotleff @ ClearSystems GmbH
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image
import subprocess
import time

# Device configuration
# Change width, height and serial address according to your display.
# Set your device type after device. The display can be rotated with rotate (2 --> 180 degrees)
width = 128
height = 64
serial = i2c(port=1, address=0x3c)
device = ssd1306(serial, rotate=2)

# Configuration of drawing parameters
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
fontSmall = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)
padding = -2

top = padding
bottom = height - padding
x = 0
i = 0

while True:
	with canvas(device) as draw:
		# Draw a black filled box to clear the image.
		draw.rectangle((0, 0, width, height), outline=0, fill=0)

		# Shell scripts for system monitoring from here:
		# https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
		cmd = "hostname -I | cut -d' ' -f1"
		IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
		cmd = 'cut -f 1 -d " " /proc/loadavg'
		CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
		cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
		MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
		cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
		Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

		# Write four lines of text.
		draw.text((x, top + 0), "Up: " + str(i) + "s", font=font, fill=255)
		draw.text((x, top + 24), "IP: " + IP, font=fontSmall, fill=255)
		draw.text((x, top + 38), "CPU load: " + CPU, font=fontSmall, fill=255)
		draw.text((x, top + 52), MemUsage, font=fontSmall, fill=255)

		time.sleep(1)
		i+=1
