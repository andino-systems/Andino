#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
from threading import Thread

import serial

from andinopy.interfaces.andino_hardware_interface import andino_hardware_interface
from andinopy.interfaces.andino_temp_interface import andino_temp_interface


class andino_x1(andino_hardware_interface, andino_temp_interface):
    def __init__(self, broad_cast_function: callable(str), port: str = "/dev/ttyAMA0", baud: int = 38400, timeout=None,
                 write_timeout: int = None, byte_size: int = serial.EIGHTBITS, parity: int = 0, stop_bits: int = 0,
                 read_size: int = 1024, encoding: str = 'ascii'):
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
        super().__init__(broad_cast_function)
        self.running = False
        self._encoding = encoding
        self._read_size = read_size
        self._serial_port = serial.Serial(port, baud, byte_size, parity, stop_bits, writeTimeout=write_timeout,
                                          timeout=timeout)
        self.from_x1 = self.handle_receive()

        def receive_thread_code(serial_port: serial.Serial, x1instance: 'andino_x1',):
            while x1instance.running:
                recv = serial_port.read(1024)
                x1instance.from_x1.send(recv)

        self._receive_thread = Thread(target=receive_thread_code, args=[self._serial_port, self])

    def start(self):
        """
        Start the x1 device after configuration
        :return:
        """
        self.running = True
        if not self._serial_port.is_open:
            self._serial_port.open()
        self._receive_thread.start()

    def stop(self):
        """
        Stop the x1 device and close all ports
        :return:
        """
        self.running = False
        if self._serial_port.is_open:
            self._serial_port.close()
        self._receive_thread.join(1)

    def _send_to_x1(self, message):
        self._serial_port.write(message.encode())

    def reset(self) -> str:
        self._send_to_x1("RESET")
        return await next(self.from_x1)

    def info(self) -> str:
        self._send_to_x1("INFO")
        return await next(self.from_x1)

    def hardware(self, mode: int) -> str:
        self._send_to_x1(f"HARD {mode}")
        return await next(self.from_x1)

    def set_polling(self, polling_time: int) -> str:
        self._send_to_x1(f"POLL {polling_time}")
        return await next(self.from_x1)

    def set_skip(self, skip_count: int) -> str:
        self._send_to_x1("SKIP")
        return await next(self.from_x1)

    def set_edge_detection(self, value: bool) -> str:
        self._send_to_x1(f"EGDE {int(value)}")
        return await next(self.from_x1)

    def set_send_time(self, send_time: int) -> str:
        self._send_to_x1(f"SEND {send_time}")
        return await next(self.from_x1)

    def set_send_broadcast_timer(self, value: bool) -> str:
        self._send_to_x1(f"CNTR {int(value)}")
        return await next(self.from_x1)

    def set_debounce(self, debouncing: int) -> str:
        self._send_to_x1(f"DEBO {debouncing}")
        return await next(self.from_x1)

    def set_power(self, value: int) -> str:
        self._send_to_x1(f"POWR {value}")
        return await next(self.from_x1)

    def set_send_relays_status(self, value: bool) -> str:
        self._send_to_x1(f"REL?")
        return await next(self.from_x1)

    def set_relay(self, relay_num: int, value: int) -> str:
        self._send_to_x1(f"REL{relay_num} {value}")
        return await next(self.from_x1)

    def pulse_relay(self, relay_num: int, value: int) -> str:
        self._send_to_x1(f"RPU{relay_num} {int(value)}")
        return await next(self.from_x1)

    def set_broadcast_on_change(self, value: bool) -> str:
        self._send_to_x1(f"CHNG {int(value)}")
        return await next(self.from_x1)

    def set_temp_broadcast_timer(self, value: int) -> str:
        self._send_to_x1(f"SENDT {value}")
        return await next(self.from_x1)

    def get_temp(self) -> str:
        self._send_to_x1(f"TEMP")
        return await next(self.from_x1)

    def set_bus(self, count: int) -> str:
        self._send_to_x1(f"TBUS {count}")
        return await next(self.from_x1)

    def get_addresses(self) -> str:
        self._send_to_x1(f"ADDRT")
        return await next(self.from_x1)

    def handle_receive(self):
        while self.running:
            recv: str = yield
            if recv.startswith(":"):
                self.broadcast(recv)
            else:
                yield recv

    def broadcast(self, recv: str):
        self.broad_cast_function(recv[4:])
