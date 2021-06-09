#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import threading

from andinopy.interfaces.rfid_keyboard_interface import rfid_keyboard_interface
import serial


class rfid_keyboard_serial(rfid_keyboard_interface):
    com_port: serial.Serial = None
    running = False
    thread = None

    def __init__(self):
        super().__init__()

    def start(self) -> None:
        self.com_port: serial.Serial = serial.Serial("COM5", 38400)
        self.running = True

        def read_thread_code(parent_obj: rfid_keyboard_serial):
            while parent_obj.running:
                char = parent_obj.com_port.read(1)
                parent_obj._on_char_received(char.decode())

        self.thread = threading.Thread(target=read_thread_code, args=[self])
        self.thread.start()

    def stop(self) -> None:
        self.running = False
        self.thread.join(timeout=1)
        self.com_port.close()

    def buzz_display(self, duration_ms: int) -> None:
        self._send_to_controller(f"buz {duration_ms}")

    def _send_to_controller(self, value: str) -> None:
        self.com_port.write(value.encode())
