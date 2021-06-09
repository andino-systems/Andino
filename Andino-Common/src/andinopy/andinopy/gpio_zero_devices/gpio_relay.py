#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import gpiozero


class gpio_relay(gpiozero.DigitalOutputDevice):
    def __init__(self, pin: int, start_config: bool = False, active_high=True):
        super().__init__(pin=pin, initial_value=start_config, active_high=active_high)

    def pulse(self, ms: int):
        self.blink(on_time=ms / 1000, n=1, background=True)
