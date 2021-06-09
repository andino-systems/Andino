#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import threading
import smbus2
import serial
from gpiozero import Button
from andinopy import log, andinoio


class andino_terminal:
    class _rfid_keyboard_handle:
        _interruptPin = 23
        _slaveAddress = 0x4
        _i2c = smbus2.SMBus(1)
        _interrupt: Button = None
        _rfid_buffer: str = ""
        _rfid_mode: bool = False

        # custom functions
        on_rfid_string: callable(str)
        on_function_button: callable(str)
        on_keyboard_button: callable(str)

        def __init__(self, on_rfid: callable(str) = None, on_function: callable(str) = None,
                     on_keyboard: callable(str) = None):
            """
            Initialize the Keyboard and RFID
            :param on_rfid: function
            :param on_function: function
            :param on_keyboard: function
            """

            self.on_rfid_string = on_rfid
            self.on_function_button = on_function
            self.on_keyboard_button = on_keyboard
            log.debug("RFID and Keyboard initialized")

        def start(self):
            """
            start the Keyboard - be sure to set custom configuration first
            :return:
            """
            self._interrupt = Button(self._interruptPin, hold_time=0.01, hold_repeat=True, pull_up=False)
            self._interrupt.when_held = self._read_i2c
            self._i2c.open(1)
            log.debug("RFID and Keyboard started")

        def stop(self):
            self._interrupt.close()
            self._i2c.close()
            log.debug("RFID and Keyboard stopped")

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
            if char_received != ' ':
                log.debug(f"received char from display: {char_received}")
                if char_received == ':':
                    if self._rfid_mode:
                        self._rfid_mode = False
                        self.on_rfid_string(self._rfid_buffer)
                        self._rfid_buffer = ""

                    else:
                        self._rfid_mode = True
                elif self._rfid_mode:
                    self._rfid_buffer += char_received
                elif 'a' <= char_received <= 'f':
                    self.on_function_button("F" + str(ord(char_received) - 96))
                elif '0' <= char_received <= '9':
                    self.on_keyboard_button(char_received)
                else:
                    function_match = {
                        '+': "UP",
                        '-': "DOWN",
                        'o': "OK",
                        'x': "ESC",
                        '<': "DEL",
                    }
                    self.on_function_button(function_match[char_received])

    class _display_handle:
        _port: serial.Serial = None
        _read_thread: threading.Thread = None
        _stop_bits: bytearray = [0xFF, 0xFF, 0xFF]

        kill_thread = False

        # custom
        serial_port: str
        serial_stop_bits: int
        serial_data_bits: int
        serial_timeout: float
        on_display_touch: callable(bytearray)
        on_display_string: callable(bytearray)

        def __init__(self, serial_port: str = "/dev/ttyAMA0", serial_baud: int = 9600, serial_stop_bits: int = 1,
                     serial_data_bits: int = 8, serial_timeout: float = None,
                     on_display_touch: callable(bytearray) = None, on_display_string: callable(bytearray) = None):
            """
            Initialize the Display
            Only Change the Serial Parts if you know what you are doing
            :param serial_port:
            :param serial_baud:
            :param serial_stop_bits:
            :param serial_data_bits:
            :param serial_timeout:
            :param on_display_touch:
            :param on_display_string:
            """
            self.serial_port = serial_port
            self.serial_baud = serial_baud
            self.serial_stop_bits = serial_stop_bits
            self.serial_data_bits = serial_data_bits
            self.serial_timeout = serial_timeout
            self.on_display_touch = on_display_touch
            self.on_display_string = on_display_string
            log.debug("Nextion device initialized")

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

            def _read_thread(handle):
                read_buffer = bytearray()
                log.debug("Nextion device listener Thread started")
                while not handle.kill_thread:
                    x = self._port.read()
                    log.debug(f"Nextion read: {x}")
                    read_buffer.append(int.from_bytes(x, "big"))
                    if read_buffer.endswith(b'\xff\xff\xff'):
                        handle.process_message(read_buffer[:-3])
                        read_buffer = bytearray()
                log.debug("Nextion device listener Thread stopped")

            _read_thread = threading.Thread(target=_read_thread, args=[self])
            _read_thread.start()
            log.debug("Nextion device started")

        def set_page(self, page: str):
            """
            :param page: goal page
            :return None
            """
            log.debug("Nextion device changed page")
            self.send_raw(f"page {page}")

        def set_text(self, obj: str, text: str):
            """
            Sets new text to nextion object
            :param obj: goal object
            :param text: new Text
            :return: None
            """
            self.set_attr(obj, "txt", f"\"{text}\"")

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

        def process_message(self, read_buffer: bytearray):
            log.debug(f"Nextion device - received message: {str(read_buffer)}")
            if read_buffer[0] == 0x65:
                if self.on_display_touch is not None:
                    self.on_display_touch(read_buffer)
            else:
                if self.on_display_string is not None:
                    self.on_display_string(read_buffer)

        def stop(self):
            log.debug("Nextion device stopped")
            self.kill_thread = True
            self._read_thread.join()
            self._port.close()

    # Part instances
    andinoio_instance: andinoio.andinoio
    display_instance: _display_handle
    rfid_keyboard_instance: _rfid_keyboard_handle

    def __init__(self,
                 andinoio_instance: andinoio.andinoio = None,
                 display_instance: _display_handle = None,
                 rfid_keyboard_instance: _rfid_keyboard_handle = None):
        """
        Create a new Terminal instance
        Can be passed preconfigured handles
        """
        log.debug("Terminal starting initialization")
        self.andinoio_instance = andinoio_instance if andinoio_instance is not None else andinoio.andinoio()
        self.display_instance = display_instance if display_instance is not None else self._display_handle()
        self.rfid_keyboard_instance = rfid_keyboard_instance \
            if rfid_keyboard_instance is not None else self._rfid_keyboard_handle()
        log.debug("Terminal device initialized")

    def start(self):
        """
        Start the terminal with the custom configuration
        :return: None
        """
        log.debug("Terminal device started")
        self.andinoio_instance.start()
        self.display_instance.start()
        self.rfid_keyboard_instance.start()
        log.debug("Terminal - everything started")

    def stop(self):
        """
        Stops and resets the terminal
        :return:
        """
        log.debug("Terminal device stopped")
        self.andinoio_instance.stop()
        self.display_instance.stop()
        self.rfid_keyboard_instance.stop()
