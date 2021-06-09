#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import smbus2
from gpiozero import Button

from andinopy import andinopy_logger
from andinopy.interfaces.rfid_keyboard_interface import rfid_keyboard_interface


class rfid_keyboard_i2c(rfid_keyboard_interface):
    _interruptPin = 23
    _slaveAddress = 0x4
    _i2c = smbus2.SMBus(1)
    _interrupt: Button = None

    def __init__(self, on_rfid: callable(str) = None, on_function: callable(str) = None,
                 on_keyboard: callable(str) = None):
        """
        Initialize the Keyboard and RFID
        :param on_rfid: function
        :param on_function: function
        :param on_keyboard: function
        """

        super().__init__()
        self.on_rfid_string = on_rfid
        self.on_function_button = on_function
        self.on_keyboard_button = on_keyboard
        andinopy_logger.debug("RFID and Keyboard initialized")

    def start(self):
        """
        start the Keyboard - be sure to set custom configuration first
        :return:
        """
        self._interrupt = Button(self._interruptPin, hold_time=0.01, hold_repeat=True, pull_up=False)
        self._interrupt.when_held = self._read_i2c
        self._i2c.open(1)
        andinopy_logger.debug("RFID and Keyboard started")

    def stop(self):
        self._interrupt.close()
        self._i2c.close()
        andinopy_logger.debug("RFID and Keyboard stopped")

    def buzz_display(self, ms: int):
        """
        Make a Buzz sound for ms
        :param ms: duration in ms
        :return: None
        """
        self._send_to_controller(f"buz {ms}")

    def _send_to_controller(self, input_string):
        self._i2c.write_block_data(self._slaveAddress, 0, input_string.encode("utf-8"))

    def _read_i2c(self):
        char_received = chr(self._i2c.read_byte(self._slaveAddress))
        self._on_char_received(char_received)
