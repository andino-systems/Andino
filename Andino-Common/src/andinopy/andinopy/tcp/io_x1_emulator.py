#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import threading
import time

import andinopy.interfaces.andino_hardware_interface
from andinopy.base_devices.andinoio import andinoio


class x1_emulator(andinopy.interfaces.andino_hardware_interface.andino_hardware_interface):

    def __init__(self, broad_cast_function: callable(str)):
        super().__init__(broad_cast_function)
        self.handle_x1_message: callable(str) = None
        self.io = andinoio()
        for i in range(len(self.io.Inputs)):
            self.io.Inputs[i].on_input = lambda x=i: self._on_input_hex(x)
        self.send_broadcast = True
        self._send_counter = True
        self._send_rel = False
        self._send_on_change = False
        self._hex_counter = [0 for i in range(len(self.io.Inputs))]
        self._polling = 10
        self._debouncing = 3
        self._skip = 0
        self._encoding = None
        self._read_size = None
        self._serial_port = None
        self._receive_thread = None
        self._send_interval = 3000
        self._running = False
        self._send_thread = threading.Thread(target=self._t_status_thread_code, args=[self])

    def start(self):
        self._running = True
        self.io.start()
        self._send_thread.start()

    def stop(self):
        self._running = False
        self._send_thread.join()
        self.io.stop()

    def _on_input_hex(self, i):
        self._hex_counter[i] = (self._hex_counter[i] + 1) % 0xFFFF
        if self._send_on_change:
            self.broad_cast_function(self.generate_broadcast_string())

    @staticmethod
    def _t_status_thread_code(parent_object: 'x1_emulator'):
        while parent_object._running:
            time.sleep(parent_object._send_interval / 1000)
            if parent_object.send_broadcast and parent_object._running:
                parent_object.broad_cast_function(parent_object.generate_broadcast_string())


    def generate_broadcast_string(self) -> str:
        status = ""
        if self._send_counter:
            status += f"{{{','.join([format(i, 'x') for i in self._hex_counter])}}}"
        status += f"{{{','.join([str(int(i)) for i in self.io.get_input_statuses()])}}}"
        if self._send_rel:
            status += f"{{{','.join([str(i.value) for i in self.io.outRel])}}}"
        return status

    def _set_input_configs(self):
        for i in self.io.Inputs:
            i.set_configs_x1_like(self._polling, self._debouncing, self._skip)

    def reset(self) -> str:
        self._hex_counter = [0 for _ in range(len(self.io.Inputs))]
        return "RESET"

    def info(self) -> str:
        return "ANDINO IO"

    def hardware(self, mode: int) -> str:
        if mode == 1:
            return "HARD 1"
        return "ERROR"

    def set_polling(self, polling_time: int) -> str:
        self._polling = polling_time
        self._set_input_configs()
        return f"POLL {polling_time}"

    def set_skip(self, skip_count: int) -> str:
        self._skip = skip_count
        self._set_input_configs()
        return f"SKIP{skip_count}"

    def set_edge_detection(self, value: bool) -> str:
        self.io.input_pull_up = [value for _ in range(len(self.io.Inputs))]
        self._set_input_configs()
        return f"EDGE {int(value)}"

    def set_send_time(self, send_time: int) -> str:
        self._send_interval = time
        return f"SEND {send_time}"

    def set_debounce(self, debouncing: int) -> str:
        self._debouncing = debouncing
        self._set_input_configs()
        return f"DEBO {int(debouncing)}"

    def set_power(self, value: int) -> str:
        return "ERROR"

    def set_send_relays_status(self, value: bool) -> str:
        self._send_rel = value
        return f"REL? {int(value)}"

    def set_relay(self, relay_num: int, value: int) -> str:
        self.io.set_relay(relay_num - 1, value)
        return f"REL{relay_num} {value}"

    def pulse_relay(self, relay_num: int, value: int) -> str:
        self.io.pulse_relays(relay_num - 1, value)
        return f"RPU{relay_num} {value}"

    def set_broadcast_on_change(self, value: bool) -> str:
        self._send_on_change = value
        return f"CHNG {int(value)}"

    def set_send_broadcast_timer(self, value: bool) -> str:
        self.send_broadcast = value
        return f"CNTR {int(value)}"

    def get_counters(self, mode: int) -> str:
        value = f"{{{','.join([format(i, 'x') for i in self._hex_counter])}}}"
        if mode > 0:
            value += f"{{{','.join([str(int(i)) for i in self.io.get_input_statuses()])}}}"
        if mode > 1:
            value += f"{{{','.join([str(i.value) for i in self.io.outRel])}}}"
        return value
