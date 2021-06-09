#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import andinopy.tcp.io_x1_emulator
from andinopy.interfaces.andino_hardware_interface import andino_hardware_interface
from andinopy.interfaces.andino_temp_interface import andino_temp_interface
from andinopy.tcp import simpletcp
from typing import Dict


class andino_tcp:

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
        self._message_counter = 0
        self.temperature_enabled = False

        self.display_enabled = display
        self.key_rfid_enabled = key_rfid
        self.oled_enabled = oled
        self.port = port
        self._message_counter = 0
        self.hardware = hardware
        self.tcpserver = simpletcp.tcp_server(port=self.port, on_message=self._i_handle_tcp_input)

        if hardware == "io":
            self.x1_instance: andino_hardware_interface = andinopy.tcp.io_x1_emulator.x1_emulator(self._o_broadcast)
        elif hardware == "x1":
            from andinopy.base_devices import andinox1
            self.x1_instance: andino_hardware_interface = andinox1.andino_x1(self._o_broadcast)
        else:
            raise AttributeError("hardware must be 'x1' or 'io")
        if temp and isinstance(self.x1_instance, andino_temp_interface):
            self.temperature_enabled = True
            self.temperature_handle: andino_temp_interface = self.x1_instance
        if self.key_rfid_enabled:
            self._init_key_rfid()
        if self.display_enabled:
            self._init_key_rfid()
        if self.oled_enabled:
            self._init_oled()

        self.assign: Dict[str, callable([str, simpletcp.tcp_server.client_handle])] = {
            'RESET': lambda x: self._i_reset(),
            'INFO': self._i_handle_andino_hardware_message,
            'HARD': self._i_handle_andino_hardware_message,
            'POLL': self._i_handle_andino_hardware_message,
            'SKIP': self._i_handle_andino_hardware_message,
            'EDGE': self._i_handle_andino_hardware_message,
            'SEND': self._i_handle_andino_hardware_message,
            'CHNG': self._i_handle_andino_hardware_message,
            'CNTR': self._i_handle_andino_hardware_message,
            'DEBO': self._i_handle_andino_hardware_message,
            'POWR': self._i_handle_andino_hardware_message,
            'REL?': self._i_handle_andino_hardware_message,
            'REL1': self._i_handle_andino_hardware_message,
            'REL2': self._i_handle_andino_hardware_message,
            'REL3': self._i_handle_andino_hardware_message,
            'REL4': self._i_handle_andino_hardware_message,
            'RPU1': self._i_handle_andino_hardware_message,
            'RPU2': self._i_handle_andino_hardware_message,
            'RPU3': self._i_handle_andino_hardware_message,
            'RPU4': self._i_handle_andino_hardware_message,
            'TBUS': self._i_handle_temp_message,
            'ADDRT': self._i_handle_temp_message,
            'SENDT': self._i_handle_temp_message,
            'TEMP': self._i_handle_temp_message,
            'BUZZ': self._i_buzz_message,
            'DISP': self._i_handle_nextion_display_message,
            'OLED': self._i_handle_oled_message,
            'SYS': self._i_handle_sys_message
        }

    def start(self):
        self.x1_instance.start()
        if self.display_enabled:
            self.display_instance.start()
        if self.key_rfid_enabled:
            self.key_rfid_instance.start()
        self.tcpserver.start()

    def stop(self):
        self.x1_instance.stop()
        if self.display_enabled:
            self.display_instance.stop()
        if self.key_rfid_enabled:
            self.key_rfid_instance.stop()
        self.tcpserver.stop()

    # region custom initializers

    def _init_oled(self):
        from andinopy.base_devices import andino_io_oled
        self.oled_instance = andino_io_oled.andino_io_oled()

    def _init_key_rfid(self):
        self.key_rfid_instance = andinopy.base_devices.rfid_keyboard_interface.rfid_keyboard_interface()
        self.key_rfid_instance.on_rfid_string = self._o_on_rfid
        self.key_rfid_instance.on_function_button = self._o_on_function_button
        self.key_rfid_instance.on_keyboard_button = self._o_on_number_button

    def _init_display(self):
        self.display_instance = andinopy.base_devices.nextion_display.display()
        self.display_instance.on_display_touch = self._o_on_display_touch
        self.display_instance.on_display_string = self._o_on_display_string

    # endregion

    # region incoming functions
    def _i_handle_tcp_input(self, tcp_in: str, client_handle: simpletcp.tcp_server.client_handle):
        func = self.assign.get(tcp_in.split(" ")[0])
        if func is None:
            client_handle.send_line("ERROR")
        func(tcp_in, client_handle)

    def _i_handle_sys_message(self, message: str):
        pass

    def _i_reset(self):
        self._message_counter = 0
        self.x1_instance.reset()

    def _i_buzz_message(self, message: str, client_handle: simpletcp.tcp_server.client_handle):
        try:
            self.key_rfid_instance.buzz_display(int(message.split(" ")[1]))
        except ValueError:
            client_handle.send_line("ERROR")

    def _i_handle_nextion_display_message(self, message: str, client_handle: simpletcp.tcp_server.client_handle):
        # DISP PAGE <page> -> Display page setzen
        # DISP TXT <obj> -> Text setzen
        # DISP ATTR <obj> <attribute> <value> -> Object Atribut setzen
        # DISP RAW <bytes in hex> -> send raw bytes to the display
        if not self.display_enabled:
            client_handle.send_line("ERROR DISPLAY DISABLED")
            return
        attributes = [i.replace("<", "").replace(">", "") for i in message.split(" ")][1:]
        call: Dict[str, callable] = {
            "PAGE": lambda: self.display_instance.set_page(attributes[1]),
            "TXT": lambda: self.display_instance.set_text(attributes[1], attributes[2]),
            "ATTR": lambda: self.display_instance.set_attr(attributes[1], attributes[2], attributes[3]),
            "RAW": lambda: self.display_instance.send_raw(attributes[1])
        }
        if attributes[0] not in call:
            client_handle.send_line("ERROR")
            return
        call[attributes[0]]()

    def _i_handle_temp_message(self, message: str, client_handle: simpletcp.tcp_server.client_handle):
        # SENDT [0| ms > 1000] -> Temperatur Meldezyklus
        # ADDRT [1|2] -> Temepraturmesser Adressen
        # TBUS [1|2] -> Bus anzahl setzen
        # TEMP        -> poll temperature once
        if not self.temperature_enabled:
            client_handle.send_line("ERROR")
            return
        else:
            if message.startswith("SENDT"):
                try:
                    client_handle.send_line(
                        self.temperature_handle.set_temp_broadcast_timer(int(message.split(" ")[1])))
                except ValueError:
                    client_handle.send_line("ERROR")
                return
            if message.startswith("ADDRT"):
                try:
                    client_handle.send_line(
                        self.temperature_handle.set_temp_broadcast_timer((int(message.split(" ")[1]))))
                except ValueError:
                    client_handle.send_line("ERROR")
                return
            if message.startswith("TBUS"):
                try:
                    client_handle.send_line(self.temperature_handle.set_bus(int(message.split(" ")[1])))
                except ValueError:
                    client_handle.send_line("ERROR")
                return
            if message.startswith("TEMP"):
                try:
                    client_handle.send_line(self.temperature_handle.get_temp())
                except ValueError:
                    client_handle.send_line("ERROR")
                return

    def _i_handle_oled_message(self, message: str, client_handle: simpletcp.tcp_server.client_handle):
        # TODO send respone to client
        if message.startswith("OLED MODE"):
            modes = message.split(" ")[2:]
            if len(modes) == 2:
                self.oled_instance.set_mode(modes[0], modes[1])
            else:
                self.oled_instance.set_mode(modes[0])
        else:
            text = [j.replace("{", "").split("}")[:-1] for j in
                    [i.replace("<", "") for i in message.replace("OLED ", "").split(">")[:-1]]]
            if len(text) == 2:
                self.oled_instance.set_text([text[0], text[1]])
            else:
                self.oled_instance.set_text(text[0])

    def _i_handle_andino_hardware_message(self, message: str, client_handle: simpletcp.tcp_server.client_handle):
        if message == "INFO":
            client_handle.send_line(self.x1_instance.info())
            return
        if message.startswith("HARD"):
            try:
                client_handle.send_line(self.x1_instance.hardware(int(message.split(" ")[1])))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("POLL"):
            try:
                client_handle.send_line(self.x1_instance.set_polling(int(message.split(" ")[1])))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("SKIP"):
            try:
                client_handle.send_line(self.x1_instance.set_skip(int(message.split(" ")[1])))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("EDGE"):
            try:
                client_handle.send_line(self.x1_instance.set_edge_detection(bool(int(message.split(" ")[1]))))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("SEND"):
            try:
                client_handle.send_line(self.x1_instance.set_send_time(int(message.split(" ")[1])))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("CHNG"):
            try:
                client_handle.send_line(self.x1_instance.set_broadcast_on_change(bool(int(message.split(" ")[1]))))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("CNTR"):
            # TODO CNTR	Send Counter - Send counter+states(1) or only states(0)
            #  (default 1) or with counter+states+relays(2)
            try:
                client_handle.send_line(self.x1_instance.get_counters(int(message.split(" ")[1])))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("DEBO"):
            try:
                client_handle.send_line(self.x1_instance.set_debounce(int(message.split(" ")[1])))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("POWR"):
            try:
                client_handle.send_line(self.x1_instance.set_power(int(message.split(" ")[1])))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("REL?"):
            try:
                client_handle.send_line(self.x1_instance.set_send_relays_status(bool(int(message.split(" ")[1]))))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("REL"):
            try:
                i, s = map(int, message[3:].split(" "))
                client_handle.send_line(self.x1_instance.set_relay(i, s))
            except ValueError:
                client_handle.send_line("ERROR")
            return
        if message.startswith("RPU"):
            try:
                i, s = map(int, message[3:].split(" "))
                client_handle.send_line(self.x1_instance.pulse_relay(i, s))
            except ValueError:
                client_handle.send_line("ERROR")
            return

    # endregion

    # region outgoing functions
    def _o_on_rfid(self, message: str):
        self.tcpserver.send_line_to_all(
            f"{self._get_and_increase_send_ctr()}@R{{{message}}}"
        )

    def _o_on_function_button(self, message: str):
        self.tcpserver.send_line_to_all(
            f":{self._get_and_increase_send_ctr()}@F{{{message}}}"
        )

    def _o_on_number_button(self, message: str):
        self.tcpserver.send_line_to_all(
            f":{self._get_and_increase_send_ctr()}@N{{{message}}}"
        )

    def _o_on_display_touch(self, message: bytes):
        self.tcpserver.send_line_to_all(
            f":{self._get_and_increase_send_ctr()}@D{{{message}}}"
        )

    def _o_on_display_string(self, message: str):
        self.tcpserver.send_line_to_all(
            f":{self._get_and_increase_send_ctr()}@D{{{message}}}"
        )

    def _o_broadcast(self, message: str):
        self.tcpserver.send_line_to_all(f":{self._get_and_increase_send_ctr()}{message}")

    # endregion
    def _get_and_increase_send_ctr(self):
        ctr = self._message_counter
        self._message_counter = (self._message_counter + 1) % 0xFFFF
        return f'{ctr:04x}'.upper()


if __name__ == "__main__":
    """
    hardware: "x1" or "io"
    port: The tcp Port the server will serve on
    oled: oled Display enabled
    temp: temperature measure enabled? (only on x1)
    key_rfid: keyboard and rfid controller enabled?
    display: display enabled?
    """
    server = andino_tcp(hardware="io", port=9999, oled=True, temp=False, key_rfid=False, display=False)
    try:
        server.start()
        input()
        input()
    finally:
        server.stop()
