import time

from andinopy import andinoterminal
import logging


class TerminalDemo:
    terminal: andinoterminal = None
    _last_keyboard: str = ""
    _last_rfid: str = ""

    def __init__(self):
        print("initializing Terminal")
        self.terminal = andinoterminal()
        self.terminal.rfid_keyboard_instance.on_function_button = self.on_function_button
        self.terminal.rfid_keyboard_instance.on_keyboard_button = self.on_keyboard_button
        self.terminal.rfid_keyboard_instance.on_rfid_string = self.on_rfid_string
        self.terminal.display_instance.on_display_touch = self.on_display_touch
        self.terminal.andinoio_instance.on_input_functions = \
            [self.input_pin for i in range(len(self.terminal.andinoio_instance.inputs_counter))]


    def __get_counters(self):
        return self.terminal.andinoio_instance.inputs_counter

    def __get_relays(self):
        return self.terminal.andinoio_instance.relays_status

    def update_terminal(self):
        print("updating Display")
        ctr = self.__get_counters()

        for i in range(len(ctr)):
            self.terminal.display_instance.set_text(f"input{i + 1}", ctr[i])
        rel_stats = ["on" if i == 1 else "off" for i in self.__get_relays()]

        for j in range(len(rel_stats)):
            self.terminal.display_instance.set_text(f"rel{j + 1}", rel_stats[j])
            self.terminal.display_instance.set_attr(f"rel{j + 1}", "pco", 1346 if rel_stats[j] == "on" else 43300)
        self.terminal.display_instance.set_text(f"rfidtxt", self._last_rfid)
        self.terminal.display_instance.set_text(f"keybrtxt", self._last_keyboard)

    def start(self):
        print("starting")
        self.terminal.start()
        self.terminal.rfid_keyboard_instance.buzz_display(500)

    def input_pin(self):
        print("pin pressed")
        self.update_terminal()

    def on_function_button(self, btn: str):
        print(f"Function Button: {btn}")
        self._last_keyboard = f"Keyboard Function Button: {btn}"
        self.update_terminal()

    def on_keyboard_button(self, btn: str):
        print(f"Keyboard Button: {btn}")
        self._last_keyboard = f"Keyboard Button: {btn}"
        self.update_terminal()

    def on_rfid_string(self, rfid: str):
        print(f"RFID: {rfid}")
        self._last_rfid = rfid
        self.update_terminal()

    def on_display_touch(self, text: bytearray):
        print(f"Display Touch: {str(text)}")
        if text[:4] == b'e\x00\x17\x01':
            self.terminal.rfid_keyboard_instance.buzz_display(500)


if __name__ == "__main__":
    log = logging.getLogger("andinopy")
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    demo = TerminalDemo()
    demo.start()
    while True:
        time.sleep(1)
