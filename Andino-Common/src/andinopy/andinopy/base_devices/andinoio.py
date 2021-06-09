#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
from typing import List

from andinopy import andinopy_logger
from andinopy.gpio_zero_devices.gpio_relay import gpio_relay
from andinopy.gpio_zero_devices.gpio_input import gpio_input


class andinoio:
    """
        Create an andinoio instance.
        Be Sure to set custom configurations before
    """

    def __init__(self, relays_start_config: bool = None, relays_active_high=True,
                 input_pull_up: List[bool] = None, inputs_polling_time: List[float] = None,
                 inputs_debounce_time: List[float] = None, on_input_functions: List[callable] = None
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
        self.outRel: List[gpio_relay] = []  # direct access to gpiozero
        self.Inputs: List[gpio_input] = []  # direct access to gpiozero

        # Custom Configuration
        for pin in self._relay_pins:
            self.outRel.append(gpio_relay(pin, relays_start_config, relays_active_high))

        if input_pull_up is None:
            input_pull_up = [True for i in range(len(self._input_pins))]
        if inputs_polling_time is None:
            inputs_polling_time = [0.005 for i in range(len(self._input_pins))]
        if inputs_debounce_time is None:
            inputs_debounce_time = [0.005 for i in range(len(self._input_pins))]
        if on_input_functions is None:
            on_input_functions = [None for i in range(len(self._input_pins))]
        for i in range(len(self._input_pins)):
            self.Inputs.append(gpio_input(self._input_pins[i],
                                          pull_up=input_pull_up[i],
                                          on_input=on_input_functions[i],
                                          debounce=inputs_debounce_time[i],
                                          hold_time=inputs_polling_time[i]))
        andinopy_logger.debug("AndinoIo initialized")

    def get_input_statuses(self):
        return [int(i.is_pressed) for i in self.Inputs]

    def start(self):
        """
        Be sure to assign Custom fields before calling
        :return: None
        """
        for i in self.Inputs:
            i.start()
        andinopy_logger.debug("AndinoIo starting")

    def reset_counter(self, input_nr: int):
        self.Inputs[input_nr].reset()

    def reset_all_counters(self):
        for i in self.Inputs:
            i.reset()
        andinopy_logger.debug("AndinoIo reset all counters")

    def set_relay(self, relays_nr: int, state: int):
        """
        :param relays_nr: goal relays
        :param state: goal state
        :return: None
        """
        andinopy_logger.debug(f"AndinoIo set relays {relays_nr}:{state}")
        if bool(state):
            self.outRel[relays_nr].on()
        else:
            self.outRel[relays_nr].off()

    def pulse_relays(self, relays_nr: int, duration: int):
        """
        opens/closes relays for duration ms
        :param relays_nr: goal relays
        :param duration: duration in ms
        :return: None
        """
        self.outRel[relays_nr].pulse(duration)

    def stop(self):
        andinopy_logger.debug("AndinoIo stopped")
        self.reset_all_counters()
        for btn in self.Inputs:
            btn.stop()
        for rel in self.outRel:
            rel.close()
