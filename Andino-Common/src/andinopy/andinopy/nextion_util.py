#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import time
import serial
import sys
import os
import re

e = bytearray([0xFF, 0xFF, 0xFF])


def get_baud_rate(dev_port: serial.Serial, diagnostics: bool = False):
    def diag_print(text: str):
        if diagnostics:
            print(text)

    for baud_rate in (2400, 4800, 9600, 19200, 38400, 57600, 115200, 921600, 512000, 256000, 250000, 230400):
        dev_port.baudrate = baud_rate
        dev_port.timeout = 3000 / baud_rate + 0.2
        diag_print(f"trying with {baud_rate} baud")
        dev_port.write(e)
        dev_port.write("connect".encode('ascii'))
        dev_port.write(e)
        r = dev_port.read(128)[:-3]
        if 'comok' in str(r):
            diag_print(f"Connected with {baud_rate} baud")
            status, unknown1, model, firmware, mcucode, nextion_serial, nextion_flashSize = str(r).strip("\xff").split(
                ',')
            if status.split(' ')[1] == "1":
                diag_print('Touchscreen: enabled')
            else:
                diag_print('Touchscreen: disabled')
            diag_print(
                f"Model:{model}\nFirmware:{firmware}\nMCU-Code:{mcucode}\nSerial:{nextion_serial}\nFlashSize:{nextion_flashSize}")
            return baud_rate
    return False


def force_max_baud(dev_port, filesize, diagnostics=False):
    def diag_print(text: str):
        if diagnostics:
            print(text)

    for baud in [921600, 512000, 256000, 250000, 230400, 115200, 57600, 38400, 31250, 19200, 9600]:
        diag_print(f"Trying {baud} baud")
        diag_print(f"SENDING: whmi-wri {filesize},{baud},0")
        dev_port.write(f"whmi-wri {filesize},{baud},0".encode("ascii"))
        dev_port.write(e)
        time.sleep(0.4)
        dev_port.baudrate = baud
        dev_port.timeout = 0.5
        time.sleep(.1)
        r = dev_port.read(1)
        if 0x05 in r:
            return True
    return False


def upload_image(dev_port, filename, filesize):
    with open(filename, 'rb') as image:
        data_count = 0
        while 1:
            data = image.read(4096)
            if len(data) < 1:
                break
            data_count += len(data)
            dev_port.timeout = 5
            dev_port.write(data)
            sys.stdout.write('\rUpload, %3.1f%%...' % (data_count / float(filesize) * 100.0))
            sys.stdout.flush()
            time.sleep(.5)
            r = dev_port.read(1)
            if 0x05 not in r:
                return False
    return True


def flash(port: str, tft_file: str):
    port = serial.Serial(port, 9600, timeout=5)
    if not port.isOpen():
        port.open()
    if not get_baud_rate(port, diagnostics=True):
        print("Baud Rate could not be specified")
        exit(1)
    file_size = os.path.getsize(tft_file)
    if not force_max_baud(port, file_size, diagnostics=True):
        print("Could not force baud rate")
        exit(1)
    if not upload_image(port, tft_file, file_size):
        print("could not upload tft File")
        exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('usage:\npython3 nextion_util.py file_to_upload.tft')
    file = sys.argv[1]
    flash("/dev/ttyAMA0", file)
    exit(0)
