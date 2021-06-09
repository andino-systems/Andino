import time
from threading import Timer
import logging
from andinopy.base_devices import terminal


class door_open:
    terminal: terminal.terminal = None
    inputMode = False
    inputString = ""
    check_pass: str = None
    password_len: int = 6
    timer: Timer = None
    # Enter your custom rfid cards here
    rfid_password = {
        "435D2E02": "123456",
        "1209381E": "987675"
    }

    def __init__(self):
        self.terminal = terminal.terminal()
        self.terminal.rfid_keyboard_instance.on_rfid_string = self.start_opening_process
        self.terminal.rfid_keyboard_instance.on_keyboard_button = self.handle_keyboard_number
        self.terminal.rfid_keyboard_instance.on_function_button = self.handle_function_button
        self.terminal.start()
        self.abort_open()

    def start_opening_process(self, rfid: str):
        log.debug(f"RFIDString: {rfid}")

        def password_timer(handle: door_open):
            log.debug(f"Password Timer ran Down")
            handle.abort_open()

        if rfid in self.rfid_password:
            self.terminal.display_instance.set_text("t_status", "PASSWORD")
            self.terminal.display_instance.set_text("t_message", "Please enter your password")
            self.inputMode = True
            self.check_pass = self.rfid_password[rfid]
            log.debug(f"RFID is in Passwords - expecting Password: {self.check_pass}")
            self.timer = Timer(10, password_timer, [self])
            self.timer.start()
        else:
            self.terminal.display_instance.set_text("t_message", "Unrecognized RFID Card")
            self.abort_open()

    def handle_function_button(self, key: str):
        if self.inputMode:
            if key == "OK":
                self.timer.cancel()
                if self.inputString == self.check_pass:
                    log.debug(f"Correct password: {self.inputString} - {self.check_pass}")
                    self.open_door()
                else:
                    log.debug(f"Wrong password: {self.inputString}")
                    self.terminal.display_instance.set_text("t_message", "WRONG PASSWORD !!!!")
                    self.abort_open()
            elif key == "DEL":
                if len(self.inputString) > 0:
                    self.inputString = self.inputString[:-1]

    def handle_keyboard_number(self, key: str):
        if self.inputMode and len(self.inputString) < self.password_len:
            self.inputString += key
            self.update_input(self.password_len)

    def update_input(self, num: int):
        self.terminal.display_instance.set_text("t_input", " ".join("*" * num) + " "
                                                + " ".join("_" * (len(self.inputString) - num)))

    def abort_open(self):
        self.inputString = ""
        self.inputMode = False
        self.terminal.rfid_keyboard_instance.buzz_display(500)
        time.sleep(1)
        self.terminal.display_instance.set_text("t_status", "CLOSED")
        self.terminal.display_instance.set_text("t_message", "Please use your RFID Card")

    def open_door(self):
        log.debug("opening Door")
        self.terminal.andinoio_instance.pulse_relays(1, 8)
        self.terminal.display_instance.set_text("t_status", "OPEN")
        self.terminal.display_instance.set_text("t_message", " ")
        time.sleep(2)
        self.abort_open()


if __name__ == "__main__":
    log = logging.getLogger("andinopy")
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)

    door = door_open()
    while 1:
        time.sleep(1)
