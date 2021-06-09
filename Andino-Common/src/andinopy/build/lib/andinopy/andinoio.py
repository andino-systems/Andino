#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
from gpiozero import Button, DigitalOutputDevice
from typing import List

from andinopy import andinopy_logger


class andinoio:
    """
        Create an andinoio instance.
        Be Sure to set custom configurations before
    """

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
        # Pins
        self._input_pins: List[int] = [13, 19, 16, 26, 20, 21]
        self._relay_pins: List[int] = [5, 6, 12]
        self._pin_power_fail: int = 18

        # Handlers
        self.outRel: List[DigitalOutputDevice] = []  # direct access to gpiozero
        self.btnInput: List[Button] = []  # direct access to gpiozero

        # States
        self.inputs_counter: List[int] = [0, 0, 0, 0, 0, 0]
        self.relays_status: List[int] = [0, 0, 0]

        # Custom Configuration
        self.relays_start_config: List[bool] = [False for _ in range(len(self.relays_status))]
        self.input_pull_up: List[bool] = [True for _ in range(len(self.inputs_counter))]  # TODO as Property

        self.inputs_polling_time: List[float] = [0.005 for _ in range(len(self.inputs_counter))]  # min_sig length ms
        # TODO as Property
        self.inputs_debounce_time: List[float] = [0.005 for _ in
                                                  range(len(self.inputs_counter))]  # interval between state change ms
        # TODO as Property
        self.on_input_functions: List[callable] = [None for _ in range(len(self.inputs_counter))]

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
        return [int(i.is_pressed) for i in self.btnInput]

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
