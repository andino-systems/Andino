#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
from andinopy import andinox1, andinoio, terminal, andino_io_oled, simpletcp
from typing import Dict


class andino_tcp:
    x1_instance: andinox1.andino_x1 = None
    oled_instance: andino_io_oled.andino_io_oled = None
    key_rfid_instance = None
    display_instance = None
    _message_counter = 0

    def __init__(self, hardware: str, port: int, oled: bool = False, temp: bool = False,
                 key_rfid: bool = False, display: bool = False):
        """
        create a new instance of the andino_tcp server
        :param hardware: "x1" or "io"
        :param port: The tcp Port the server will serve on
        :param oled: oled Display enabled
        :param temp: temperature measure enabled? (only on x1)
        :param key_rfid: keyboard and rfid controller enabled?
        :param display: display enabled?
        """
        self.display_enabled = display
        self.key_rfid_enabled = key_rfid
        self.temp_enabled = temp
        self.oled_enabled = oled
        self.port = port
        self._message_counter = 0
        self.hardware = hardware
        self.tcpserver = simpletcp.tcp_server()

        if hardware == "io":
            self._init_io()
        elif hardware == "x1":
            self._init_x1()
        else:
            raise AttributeError("hardware must be 'x1' or 'io")
        if hardware == "io" and self.temp_enabled:
            raise AttributeError("temperature is only supported on x1")
        if hardware == "x1" and (self.key_rfid_enabled or self.display_enabled or self.oled_enabled):
            raise AttributeError(" RFID, Display ror OLED are only supported on x1")
        if self.key_rfid_enabled:
            self._init_key_rfid()
        if self.display_enabled:
            self._init_key_rfid()
        if self.oled_enabled:
            self._init_oled()

        self.assign: Dict[str, callable(str)] = {
            'RESET': lambda x: self._i_reset(),
            'INFO': self.x1_instance.send_to_x1,
            'HARD': self.x1_instance.send_to_x1,
            'POLL': self.x1_instance.send_to_x1,
            'SKIP': self.x1_instance.send_to_x1,
            'EDGE': self.x1_instance.send_to_x1,
            'SEND': self.x1_instance.send_to_x1,
            'CHNG': self.x1_instance.send_to_x1,
            'CNTR': self.x1_instance.send_to_x1,
            'DEBO': self.x1_instance.send_to_x1,
            'POWR': self.x1_instance.send_to_x1,
            'REL?': self.x1_instance.send_to_x1,
            'REL1': self.x1_instance.send_to_x1,
            'REL2': self.x1_instance.send_to_x1,
            'REL3': self.x1_instance.send_to_x1,
            'REL4': self.x1_instance.send_to_x1,
            'RPU1': self.x1_instance.send_to_x1,
            'RPU2': self.x1_instance.send_to_x1,
            'RPU3': self.x1_instance.send_to_x1,
            'RPU4': self.x1_instance.send_to_x1,
            'TBUS': self._i_handle_temp_message,
            'ADDRT': self._i_handle_temp_message,
            'SENDT': self._i_handle_temp_message,
            'TEMP': self._i_handle_temp_message,
            'BUZZ': self._i_buzz_message,
            'DISP': self._i_handle_nextion_display_message,
            'OLED': self._i_handle_oled_message,
            'SYS': self._i_handle_sys_message
        }

    # region custom initializers
    def _init_x1(self):
        self.x1_instance = andinox1.andino_x1()
        self.x1_instance.handle_x1_message = self._o_x1_message
        pass

    def _init_io(self):
        self.x1_instance = andinoio.x1_emulator()
        self.x1_instance.handle_x1_message = self._o_x1_message

    def _init_oled(self):
        self.oled_instance = andino_io_oled.andino_io_oled()
        pass

    def _init_key_rfid(self):
        self.key_rfid_instance = terminal.rfid_keyboard()
        self.key_rfid_instance.on_rfid_string = self._o_on_rfid
        self.key_rfid_instance.on_function_button = self._o_on_function_button
        self.key_rfid_instance.on_keyboard_button = self._o_on_number_button

    def _init_display(self):
        self.display_instance = terminal.display()
        self.display_instance.on_display_touch = self._o_on_display_touch
        self.display_instance.on_display_string = self._o_on_display_string

    # endregion

    # region incoming functions
    def _i_handle_tcp_input(self, tcp_in: str):
        func = self.assign.get(tcp_in.split(" ")[0])
        if func is None:
            self._o_error("NOT SUPPORTED")
        func(tcp_in)

    def _i_handle_sys_message(self, message: str):

        pass

    def _i_reset(self):
        self._message_counter = 0
        self.x1_instance.send_to_x1("RESET")

    def _i_buzz_message(self, message: str):
        try:
            self.key_rfid_instance.buzz_display(int(message.split(" ")[1]))
        except ValueError:
            self._o_error("ERROR")

    def _i_handle_nextion_display_message(self, message: str):
        # DISP PAGE <page> -> Display page setzen
        # DISP TXT <obj> -> Text setzen
        # DISP ATTR <obj> <attribute> <value> -> Object Atribut setzen
        # DISP RAW <bytes in hex> -> send raw bytes to the display
        if not self.display_enabled:
            self._o_error("ERROR DISPLAY DISABLED")
            return
        attributes = [i.replace("<", "").replace(">", "") for i in message.split(" ")][1:]
        call: Dict[str, callable] = {
            "PAGE": lambda: self.display_instance.set_page(attributes[1]),
            "TXT": lambda: self.display_instance.set_text(attributes[1], attributes[2]),
            "ATTR": lambda: self.display_instance.set_attr(attributes[1], attributes[2], attributes[3]),
            "RAW": lambda: self.display_instance.send_raw(attributes[1])
        }
        if attributes[0] not in call:
            self._o_error("ERROR")
            return
        call[attributes[0]]()

    def _i_handle_temp_message(self, message: str):
        # SENDT [0| ms > 1000] -> Temperatur Meldezyklus
        # ADDRT [1|2] -> Temepraturmesser Adressen
        # TBUS [1|2] -> Bus anzahl setzen
        # TEMP        -> poll temperature once
        if not self.temp_enabled:
            self._o_error("ERROR TEMP NOT ENABELD")
            return
        else:
            self.x1_instance.send_to_x1(message)

    def _i_handle_oled_message(self, message: str):
        if message.startswith("OLED MODE"):
            modes = message.split(" ")[2:]
            if len(modes) == 2:
                self.oled_instance.set_mode(2, modes[0], modes[1])
            else:
                self.oled_instance.set_mode(1, modes[0])
        else:
            text = [j.replace("{", "").split("}")[:-1] for j in
                    [i.replace("<", "") for i in message.replace("OLED ", "").split(">")[:-1]]]
            if len(text) == 2:
                self.oled_instance.set_text(text[0], text[1])
            else:
                self.oled_instance.set_text(text[0])

    # endregion

    # region outgoing functions

    # Nachrichten des Interface
    # message ->			: counter info
    # counter ->			hex sendenummer %FFFF (0000...FFFF)
    # info -> 			standart_x1 | temp | display | funktionstaste | nummerische taste | rfid
    # temp -> 			@T{busNr}{temp1,temp2}
    # display -> 			@D{bytes}
    # funktionstaste -> 	@F{taste}
    # nummerische taste ->@N{taste}
    # rfid	-> 			@R{hex rfid string}
    #
    #
    # :0000{     X1 IO Message
    # :0000@T{}  @ ex

    def _o_on_rfid(self, message: str):
        self.tcpserver.send_to_all(
            f":{self._get_and_increase_send_ctr()}@R{{{message}}}"
        )

    def _o_on_function_button(self, message: str):
        self.tcpserver.send_to_all(
            f":{self._get_and_increase_send_ctr()}@F{{{message}}}"
        )

    def _o_on_number_button(self, message: str):
        self.tcpserver.send_to_all(
            f":{self._get_and_increase_send_ctr()}@N{{{message}}}"
        )

    def _o_x1_message(self, message: str):
        self.tcpserver.send_to_all(
            f":{self._get_and_increase_send_ctr()}{message}"
        )

    def _o_on_display_touch(self, message: bytes):
        self.tcpserver.send_to_all(
            f":{self._get_and_increase_send_ctr()}@D{{{message}}}"
        )

    def _o_on_display_string(self, message: str):
        self.tcpserver.send_to_all(
            f":{self._get_and_increase_send_ctr()}@D{{{message}}}"
        )

    def _o_error(self, message: str):
        self.tcpserver.send_to_all(message)

    # endregion

    def _get_and_increase_send_ctr(self):
        ctr = self._message_counter
        self._message_counter = (self._message_counter + 1) % 0xFFFF
        return ctr
