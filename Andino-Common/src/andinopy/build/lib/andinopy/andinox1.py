#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
from threading import Thread

import serial


class andino_x1:
    def __init__(self, port: str = "/dev/ttyAMA0", baud: int = 38400, timeout=None, write_timeout: int = None,
                 byte_size: int = serial.EIGHTBITS, parity: int = 0, stop_bits: int = 0, read_size: int = 1024,
                 encoding: str = 'ascii'):
        """
        Generate the serial Port for communication with the x1
        :param port: ie. /dev/tty/AMA0
        :param baud: standart Baud Rates
        :param timeout: send timeout
        :param write_timeout: write timeout
        :param byte_size: size of a byte ie 4,7,8
        :param parity: bit parity
        :param stop_bits: how many stop bits
        :param read_size: size in byte to read at once (max)
        :param encoding: ie ascii or utf-8
        """
        self._encoding = encoding
        self._read_size = read_size
        self._serial_port = serial.Serial(port, baud, byte_size, parity, stop_bits, writeTimeout=write_timeout,
                                          timeout=timeout)
        self.handle_x1_message: callable(str) = lambda x: print(x.decode(self._encoding))

        def receive_thread_code(serial_port: serial.Serial, event_handler: callable(str), read_len: int):
            while 1:
                recv = serial_port.read(read_len)
                event_handler(recv)

        self._receive_thread = Thread(target=receive_thread_code, args=[self._serial_port, self.handle_x1_message])

    def start(self):
        """
        Start the x1 device after configuration
        :return:
        """
        if not self._serial_port.is_open:
            self._serial_port.open()
        self._receive_thread.start()

    def stop(self):
        """
        Stop the x1 device and close all ports
        :return:
        """
        if self._serial_port.is_open:
            self._serial_port.close()
        self._receive_thread.join(1)

    def send_to_x1(self, message: str):
        """
        encodes the message and sends it to the x1
        :param message: message to be encoded and sent
        :return:
        """
        self._serial_port.write(message.encode(self._encoding))
