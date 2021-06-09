#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import sys

from andinopy import andinopy_logger
from andinopy.base_devices import andinoio
from andinopy.base_devices.nextion_display import display
from andinopy.interfaces.rfid_keyboard_interface import rfid_keyboard_interface


class terminal:
    # Part instances
    andinoio_instance: andinoio.andinoio
    display_instance: 'display'
    rfid_keyboard_instance: 'rfid_keyboard_interface'

    def __init__(self,
                 andinoio_instance: andinoio.andinoio = None,
                 display_instance: 'display' = None,
                 rfid_keyboard_instance: 'rfid_keyboard_interface' = None):
        """
        Create a new Terminal instance
        Can be passed preconfigured handles
        """
        if sys.platform == "linux":
            from andinopy.base_devices.rfid_keyboard.rfid_keyboard_i2c import rfid_keyboard_i2c
            self.rfid_keyboard_instance = rfid_keyboard_instance \
                if rfid_keyboard_instance is not None else rfid_keyboard_i2c()
        else:
            from andinopy.base_devices.rfid_keyboard.rfid_keyboard_serial import rfid_keyboard_serial
            self.rfid_keyboard_instance = rfid_keyboard_instance \
                if rfid_keyboard_instance is not None else rfid_keyboard_serial()

        andinopy_logger.debug("Terminal starting initialization")
        self.andinoio_instance = andinoio_instance if andinoio_instance is not None else andinoio.andinoio()
        self.display_instance = display_instance if display_instance is not None else display()

        andinopy_logger.debug("Terminal device initialized")

    def start(self):
        """
        Start the terminal with the custom configuration
        :return: None
        """
        andinopy_logger.debug("Terminal device started")
        self.andinoio_instance.start()
        self.display_instance.start()
        self.rfid_keyboard_instance.start()
        andinopy_logger.debug("Terminal - everything started")

    def stop(self):
        """
        Stops and resets the terminal
        :return:
        """
        andinopy_logger.debug("Terminal device stopped")
        self.andinoio_instance.stop()
        self.display_instance.stop()
        self.rfid_keyboard_instance.stop()
