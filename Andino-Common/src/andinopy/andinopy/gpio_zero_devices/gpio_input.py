#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
from typing import Optional

import gpiozero


class gpio_input:
    def __init__(self, pin: int,
                 hold_time: float = 0.005,
                 debounce: float = 0.005,
                 on_input: callable = None,
                 pull_up: bool = False):
        self._pin: int = pin
        self._pull_up: bool = pull_up
        self._hold_time: float = hold_time
        self._bounce_time: float = debounce
        self.on_input: callable = on_input
        self._button: Optional[gpiozero.Button] = None
        self._counter: int = 0
        self._running: bool = False

    def start(self):
        self._running = True
        self._rebuild_button()

    def stop(self):
        self._running = False
        if self._button:
            self._button.close()

    # region pin
    @property
    def pin(self) -> int:
        return self._pin

    @pin.setter
    def pin(self, value: int):
        self._pin = value
        if self._running:
            self._rebuild_button()

    # endregion

    # region pull_up
    @property
    def pull_up(self) -> bool:
        return self._pull_up

    @pull_up.setter
    def pull_up(self, value: bool):
        self._pull_up = value
        if self._running:
            self._rebuild_button()

    # endregion

    # region hold_time
    @property
    def hold_time(self) -> float:
        return self._hold_time

    @hold_time.setter
    def hold_time(self, value: float):
        self._hold_time = value
        if self._running:
            self._button.hold_time = value

    # endregion

    # region bounce_time
    @property
    def bounce_time(self) -> float:
        return self._hold_time

    @bounce_time.setter
    def bounce_time(self, value: float):
        self._bounce_time = value
        if self._running:
            self._rebuild_button()

    # endregion

    # region counter
    @property
    def counter(self):
        return self._counter

    def reset(self):
        self._counter = 0

    # endregion

    @property
    def is_pressed(self):
        if self._running:
            return self._button.is_active
        return False

    def _input(self):
        self._counter += 1
        if self.on_input is not None:
            self.on_input()

    def set_configs_x1_like(self, polling, debouncing, skip):
        self.hold_time = polling * skip
        self.bounce_time = polling * debouncing

    def _rebuild_button(self):
        if self._button:
            self._button.close()
        self._button = gpiozero.Button(pin=self._pin,
                                       hold_time=self._hold_time,
                                       pull_up=self._pull_up,
                                       bounce_time=self._bounce_time)
        self._button.when_pressed = self._input

