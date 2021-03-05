#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import threading
import time
from gpiozero import Button, DigitalOutputDevice
from typing import List, Dict
from andinopy import andinopy_logger, andinox1


class andinoio:
    """
        Create an andinoio instance.
        Be Sure to set custom configurations before
    """
    # Pins
    _input_pins: List[int] = [13, 19, 16, 26, 20, 21]
    _relay_pins: List[int] = [5, 6, 12]
    _pin_power_fail: int = 18

    # Handlers
    outRel: List[DigitalOutputDevice] = []  # direct access to gpiozero
    btnInput: List[Button] = []  # direct access to gpiozero

    # States
    inputs_counter: List[int] = [0, 0, 0, 0, 0, 0]
    relays_status: List[int] = [0, 0, 0]

    # Custom Configuration
    relays_start_config: List[bool] = [False for i in range(len(relays_status))]
    input_pull_up: List[bool] = [True for j in range(len(inputs_counter))]

    inputs_polling_time: List[float] = [0.005 for k in range(len(inputs_counter))]  # min_sig length ms
    inputs_debounce_time: List[float] = [0.005 for m in range(len(inputs_counter))]  # interval between state change ms
    on_input_functions: List[callable] = [None for n in range(len(inputs_counter))]

    def __init__(self, relays_start_config: List[bool] = None, input_pull_up: List[bool] = None,
                 inputs_polling_time: List[float] = None, inputs_debounce_time: List[float] = None,
                 on_input_functions: List[callable] = None
                 ):
        """
        Initialize a new AndinoIo Instance
        :param relays_start_config:
        :param input_pull_up:
        :param inputs_polling_time:
        :param inputs_debounce_time:
        :param on_input_functions:
        """
        if relays_start_config is not None:
            self.relays_start_config = relays_start_config
        if input_pull_up is not None:
            self.input_pull_up = input_pull_up
        if inputs_polling_time is not None:
            self.inputs_polling_time = inputs_polling_time
        if inputs_debounce_time is not None:
            self.inputs_polling_time = inputs_polling_time
        if on_input_functions is not None:
            self.on_input_functions = on_input_functions
        andinopy_logger.debug("AndinoIo initialized")

    def get_input_statuses(self):
        return [int(i.is_active()) for i in self.btnInput]

    def start(self):
        """
        Be sure to assign Custom fields before calling
        :return: None
        """
        andinopy_logger.debug("AndinoIo starting")
        for pin in self._relay_pins:
            self.outRel.append(DigitalOutputDevice(pin, active_high=True, initial_value=False))

            # init inputs
        for i in range(len(self._input_pins)):
            temp_button = Button(self._input_pins[i], hold_time=self.inputs_polling_time[i],
                                 bounce_time=self.inputs_debounce_time[i], pull_up=self.input_pull_up[i])
            temp_button.when_pressed = lambda x=i: self.on_input(x)
            self.btnInput.append(temp_button)
        andinopy_logger.debug("AndinoIo started")

    def reset_counter(self, input_nr: int):
        self.inputs_counter[input_nr] = 0

    def reset_all_counters(self):
        self.inputs_counter = [0 for _ in range(len(self.inputs_counter))]
        andinopy_logger.debug("AndinoIo reset all counters")

    def set_relay(self, relays_nr: int, state: int):
        """
        :param relays_nr: goal relays
        :param state: goal state
        :return: None
        """
        andinopy_logger.debug(f"AndinoIo set relays {relays_nr}:{state}")
        if state == 1:
            self.outRel[relays_nr].on()
        elif state == 0:
            self.outRel[relays_nr].off()
        self.relays_status[relays_nr] = state

    def pulse_relays(self, relays_nr: int, duration: int):
        """
        opens/closes relays for duration ms
        :param relays_nr: goal relays
        :param duration: duration in ms
        :return: None
        """
        self.outRel[relays_nr].blink(on_time=duration, n=1, background=True)

    def on_input(self, input_nr: int):
        self.inputs_counter[input_nr] += 1
        if self.on_input_functions[input_nr] is not None:
            self.on_input_functions[input_nr]()

    def stop(self):
        andinopy_logger.debug("AndinoIo stopped")
        self.reset_all_counters()
        for btn in self.btnInput:
            btn.close()
        for rel in self.outRel:
            rel.close()


class x1_emulator(andinox1.andino_x1):
    handle_x1_message: callable(str) = None
    io = andinoio()
    _send_auto = True
    _send_counter = True
    _send_rel = False
    _send_on_change = False
    _hex_counter = [0 for i in range(len(io.on_input_functions))]
    _poll = 10
    _debo = 3
    _skip = 0

    def __init__(self):
        super().__init__()
        self._encoding = None
        self._read_size = None
        self._serial_port = None
        self._receive_thread = None
        self._send_interval = 3000
        self._running = True
        self._send_thread = threading.Thread(target=self._t_status_thread_code, args=[self])
        self.assign: Dict[str, callable([])] = {
            'RESET': self._i_reset,
            'INFO': self._i_info,
            'HARD': self._i_hard,
            'POLL': self._i_poll,
            'SKIP': self._i_skip,
            'EDGE': self._i_edge,
            'SEND': self._i_send,
            'CHNG': self._i_chng,
            'CNTR': self._i_cntr,
            'DEBO': self._i_debo,
            'POWR': self._i_powr,
            'REL?': self._i_send_rel,
            'REL1': lambda x: self._i_set_rel(0, x),
            'REL2': lambda x: self._i_set_rel(1, x),
            'REL3': lambda x: self._i_set_rel(2, x),
            'REL4': lambda x: self._i_set_rel(3, x),
            'RPU1': lambda x: self._i_pulse_rel(0, x),
            'RPU2': lambda x: self._i_pulse_rel(1, x),
            'RPU3': lambda x: self._i_pulse_rel(2, x),
            'RPU4': lambda x: self._i_pulse_rel(3, x)
        }

    def _i_reset(self, message: str):
        """
        reset all counters
        :param message:
        :return:
        """
        self._hex_counter = [0 for _ in range(len(self.io.on_input_functions))]
        pass

    def _i_info(self, message: str):
        # TODO
        pass

    def _i_hard(self, message: str):
        if message != "HARD 1":
            self._o_send_message("ERROR")
        else:
            self._o_send_message("HARD 1")

    def _i_poll(self, message: str):
        try:
            self._poll = int(message)
            self._set_input_configs()
        except ValueError:
            self._o_send_message("ERROR")

    def _i_skip(self, message: str):
        try:
            self._skip = int(message)
            self._set_input_configs()
        except ValueError:
            self._o_send_message("ERROR")

    def _i_debo(self, message: str):
        try:
            self._debo = int(message)
            self._set_input_configs()
        except ValueError:
            self._o_send_message("ERROR")

    def _i_edge(self, message: str):
        # TODO
        pass

    def _i_send(self, message: str):
        try:
            self._send_interval = int(message)
            self._o_send_message(f"REL? {message}")
        except ValueError:
            self._o_send_message("ERROR")

    def _i_chng(self, message: str):
        try:
            self._send_on_change = bool(int(message))
            self._o_send_message(f"CHNG {message}")
        except ValueError:
            self._o_send_message("ERROR")

    def _i_cntr(self, message: str):
        try:
            self._send_counter = bool(int(message))
            self._o_send_message(f"CNTR {message}")
        except ValueError:
            self._o_send_message("ERROR")

    def _i_powr(self, message: str):
        self._o_send_message("ERROR")

    def _i_send_rel(self, message: str):
        try:
            self._send_rel = bool(int(message))
            self._o_send_message(f"REL? {message}")
        except ValueError:
            self._o_send_message("ERROR")

    def start(self):
        self._running = True
        self._send_thread.start()
        self.io.start()

    def stop(self):
        self._running = False
        self._send_thread.join(1)
        self.io.stop()

    def send_to_x1(self, message: str):
        # dont send to x1 but emulate the command on andinoio
        func, instruction = message.split(" ")[0:1]
        self.assign[func](instruction)

    def _i_set_rel(self, i: int, message: str):
        try:
            state = int(message)
            self.io.set_relay(i, state)
        except ValueError:
            self._o_send_message("ERROR")

    def _i_pulse_rel(self, i: int, message: str):
        try:
            state = int(message)
            self.io.pulse_relays(i, state)
        except ValueError:
            self._o_send_message("ERROR")

    def _on_input_hex(self, i):
        self._hex_counter[i] += (self._hex_counter[i] + 1) % 0xFFFF
        if self._send_on_change:
            self._o_send_message(self._o_generate_status())

    def _o_send_message(self, message: str):
        self.handle_x1_message(message)

    def _o_generate_status(self):
        status = ""
        if self._send_counter:
            status += f"{{{','.join([format(i,'x') for i in self._hex_counter])}}}"
        status += f"{{{','.join([str(int(i)) for i in self.io.get_input_statuses()])}}}"
        if self._send_rel:
            status += f"{{{','.join([str(i) for i in self.io.relays_status])}}}"
        return status

    def _t_status_thread_code(self, parent_object: 'x1_emulator'):
        while parent_object._running:
            if self._send_auto:
                parent_object._o_send_message(parent_object._o_generate_status())
            time.sleep(parent_object._send_interval / 1000)

    def _set_input_configs(self):
        # DEBO - Sets the debounce count. The signal has to be stable for nn polls
        # POLL - Sets the sampling cycle of the digital inputs [in ms]
        # SKIP - Skip n Scans after pulse recognized

        # gpiozero inputs_debounce_time ->
        # If None (the default), no software bounce compensation will be performed.Otherwise, this is the length of time
        # (in seconds) that the component will ignore changes in state after an initial change.
        for i in range(len(self.io.inputs_debounce_time)):
            self.io.inputs_debounce_time[i] = self._poll*self._debo

        # gpiozero inputs_polling_time ->
        # The length of time (in seconds) to wait after the device is activated, until executing the when_held handler.
        # If hold_repeat is True, this is also the length of time between invocations of when_held.
        for i in range(len(self.io.inputs_polling_time)):
            self.io.inputs_polling_time[i] = self._poll*self._skip
        self.io.stop()
        self.io.start()
