#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import sys
import time
from unittest import TestCase
import unittest
from andinopy.interfaces.rfid_keyboard_interface import rfid_keyboard_interface


def get_rfid_keyboard():
    if sys.platform == "linux":
        from andinopy.base_devices.rfid_keyboard.rfid_keyboard_i2c import rfid_keyboard_i2c
        return rfid_keyboard_i2c()
    else:
        from andinopy.base_devices.rfid_keyboard.rfid_keyboard_serial import rfid_keyboard_serial
        return rfid_keyboard_serial()


class test_key_rfid(TestCase):
    def test_number_keys(self):
        rfid_keyboard: rfid_keyboard_interface = get_rfid_keyboard()
        expected = [str(i) for i in range(0, 10)]
        real = []

        def keyboard_button(char):
            print(char, end="")
            real.append(char)

        rfid_keyboard.on_keyboard_button = keyboard_button
        try:
            print("Press Buttons 0 to 9 in ascending order")
            rfid_keyboard.start()
            while len(real) != len(expected):
                time.sleep(0.1)
            self.assertEqual(expected, real)

        finally:
            rfid_keyboard.stop()

    def test_function_buttons(self):
        rfid_keyboard: rfid_keyboard_interface = get_rfid_keyboard()
        expected = ["F" + str(i) for i in range(1, 7)]
        real = []

        def keyboard_button(char):
            print(char, end="")
            real.append(char)

        rfid_keyboard.on_function_button = keyboard_button
        try:
            print("Press Buttons F1 to F6 in ascending order")
            rfid_keyboard.start()
            while len(real) != len(expected):
                time.sleep(0.1)
            self.assertEqual(expected, real)
        finally:
            rfid_keyboard.stop()

    def test_buzz(self):
        rfid_keyboard: rfid_keyboard_interface = get_rfid_keyboard()
        try:
            rfid_keyboard.start()
            rfid_keyboard.buzz_display(1000)
            self.assertEqual(input("Did you hear the buzz? y/n"), "y")
        finally:
            rfid_keyboard.stop()

    def test_rfid(self):
        rfid_keyboard: rfid_keyboard_interface = get_rfid_keyboard()
        rfids = []

        def on_rfid(rfid):
            print(rfid)
            rfids.append(rfid)

        try:
            rfid_keyboard.on_rfid_string = on_rfid
            rfid_keyboard.start()
            print("Scan RFID-Card")
            while len(rfids) == 0:
                time.sleep(0.1)
            self.assertIn(rfids[0], ["2457002B", "63915203", "A97784C1"])
        finally:
            rfid_keyboard.stop()
