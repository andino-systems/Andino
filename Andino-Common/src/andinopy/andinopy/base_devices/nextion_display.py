#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import threading
import time

import serial

from andinopy import andinopy_logger


def nextion_exception(message):
    raise Exception(f"NEXTION - {message}")


nextion_codes = {
    0x0: lambda: print(""),
    0x1: lambda: nextion_exception("Invalid Command"),
    0x2: lambda: nextion_exception("Invalid ComponentID in last instruction"),
    0x3: lambda: nextion_exception("Invalid PageID in last instruction"),
    0x4: lambda: nextion_exception("Invalid PictureID in last instruction"),
    0x5: lambda: nextion_exception("Invalid FileID in last instruction"),
    0x6: lambda: nextion_exception("Invalid File Operation"),
    0x9: lambda: nextion_exception("CRC Check failed"),
    0x11: lambda: nextion_exception("Invalid BaudRate setting"),
    0x12: lambda: nextion_exception("Invalid Waveform or Channel#"),
    0x1A: lambda: nextion_exception("Invalid Variable Operation"),
    0x1B: lambda: nextion_exception("Incompatible Variable Types"),
    0x1C: lambda: nextion_exception("Attribute Assigment failed"),
    0x1E: lambda: nextion_exception("Invalid Number of Parameters"),
    0x1F: lambda: nextion_exception("IO Operation failed"),
    0x20: lambda: nextion_exception("Invalid Escape Character used"),
    0x23: lambda: nextion_exception("Variable Name too long."
                                    "Max length is 29 characters: 14 for page + “.” + 14 for component."),
    0x24: lambda: nextion_exception("Serial Buffer overflow"),
}


class display:
    _port: serial.Serial = None
    _read_thread: threading.Thread = None
    _stop_bits: bytearray = [0xFF, 0xFF, 0xFF]

    def __init__(self, serial_port: str = "/dev/ttyAMA0", serial_baud: int = 9600, serial_stop_bits: int = 1,
                 serial_data_bits: int = 8, serial_timeout: float = None,
                 on_display_touch: callable([int, int, int]) = None, on_display_base: callable(bytearray) = None):
        """
        https://nextion.tech/instruction-set/#s6
        Initialize the Display
        Only Change the Serial Parts if you know what you are doing
        :param serial_port:
        :param serial_baud:
        :param serial_stop_bits:
        :param serial_data_bits:
        :param serial_timeout:
        :param on_display_touch:
        :param on_display_base:
        """
        self.on_auto_sleep_mode_leave: callable = None
        self.on_auto_sleep_mode_enter: callable = None
        self.serial_port = serial_port
        self.serial_baud = serial_baud
        self.serial_stop_bits = serial_stop_bits
        self.serial_data_bits = serial_data_bits
        self.serial_timeout = serial_timeout
        self.on_display_touch: callable(bytearray) = on_display_touch
        self.on_display_string: callable(bytearray) = on_display_base
        self._debug_level = 3
        self.running = False
        self.requested_value = None
        andinopy_logger.debug("Nextion device initialized")

    def start(self):
        """
        Start the Device with specified parameters
        Be sure to set custom parameters before starting
        :return: None
        """
        self._port = serial.Serial(port=self.serial_port, baudrate=self.serial_baud, stopbits=self.serial_stop_bits,
                                   bytesize=self.serial_data_bits, timeout=self.serial_timeout)
        if not self._port.is_open:
            self._port.open()
        self.running = True

        def _read_thread(handle: display):
            read_buffer = bytearray()
            andinopy_logger.debug("Nextion device listener Thread started")
            while handle.running:
                x = self._port.read()
                andinopy_logger.debug(f"Nextion read: {x}")
                read_buffer.append(int.from_bytes(x, "big"))
                if read_buffer.endswith(b'\xff\xff\xff'):
                    handle.from_nextion(read_buffer[:-3])
                    read_buffer = bytearray()

            andinopy_logger.debug("Nextion device listener Thread stopped")

        self._read_thread = threading.Thread(target=_read_thread, args=[self])
        self._read_thread.start()
        andinopy_logger.debug("Nextion device started")

    def get_attr(self, attr_name):
        self.send_raw(f"get {attr_name}")
        return self.get_request()

    def get_request(self):
        while self.requested_value is None and self.running:
            time.sleep(0.01)
        x = self.requested_value
        self.requested_value = None
        return x

    def set_page(self, page: str):
        """
        :param page: goal page
        :return None
        """
        andinopy_logger.debug("Nextion device changed page")
        self.send_raw(f"page {page}")

    def set_text(self, obj: str, text: str):
        """
        Sets new text to nextion object
        :param obj: goal object
        :param text: new Text
        :return: None
        """
        self.set_attr(obj, "txt", f"\"{text}\"")

    def set_debug_level(self, level: int):
        self._debug_level = level
        self.send_raw(f"bkcmd={level}")

    def reset(self):
        self.send_raw("reset")

    def set_attr(self, obj: str, atr: str, val: str):
        """
        Sets an attribute of a nextion object
        :param obj: goal object
        :param atr: goal attribute
        :param val: new attribute value
        :return:
        """
        self.send_raw(f"{obj}.{atr}={val}")

    def send_raw(self, text: str):
        """
        send raw Text to the nextion display
        :param text:
        :return:
        """
        self._port.write(text.encode("ascii"))
        self._port.write(self._stop_bits)

    def stop(self):
        andinopy_logger.debug("Nextion device stopped")
        self.running = False
        self._read_thread.join(0.1)
        time.sleep(1)
        if self._port.is_open:
            self._port.close()

    def from_nextion(self, read_buffer: bytearray):
        # print(read_buffer)
        if read_buffer[0:3] == b"\x00\x00\x00" or read_buffer[0] == 0x88:
            # Started
            return
        if read_buffer[0] in nextion_codes:
            nextion_codes[read_buffer[0]]()
            return

        if read_buffer[0] == 0x65:
            if self.on_display_touch is not None:
                # PAGE, Object ID, 1-PRESS 0-RELEASE
                self.on_display_touch(int(read_buffer[1]), int(read_buffer[2]), int(read_buffer[3]))
            return
        if read_buffer[0] == 0x71:
            # Numerical Data:
            self.requested_value = int(read_buffer[1]) \
                                   + (int(read_buffer[2]) * 256) \
                                   + (int(read_buffer[3]) * 65536) \
                                   + (int(read_buffer[4]) * 16777216)
            return
        if read_buffer[0] == 0x70:
            self.requested_value = read_buffer[1:].decode(encoding="ascii")
            return

        if read_buffer[0] == 0x66:
            # Page Number
            self.requested_value = int(read_buffer[2])
            return

        if read_buffer[0] == 0x86:
            self.on_auto_sleep_mode_enter()
            return
        if read_buffer[0] == 0x87:
            self.on_auto_sleep_mode_leave()

        else:
            if self.on_display_string is not None:
                self.on_display_string(read_buffer)
