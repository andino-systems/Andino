#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import abc
from andinopy import andinopy_logger


class rfid_keyboard_interface(abc.ABC):
    on_rfid_string = None
    on_function_button = None
    on_keyboard_button = None

    def __init__(self):
        self._rfid_buffer: str = ""
        self._rfid_mode: bool = False

    @abc.abstractmethod
    def start(self) -> None:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def stop(self) -> None:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def buzz_display(self, duration_ms: int) -> None:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def _send_to_controller(self, value: str) -> None:
        raise NotImplementedError("meta class method not overwritten")

    def _on_char_received(self, char_received: str):
        if char_received != ' ' and char_received != '':
            andinopy_logger.debug(f"received char from display: {char_received}")
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
