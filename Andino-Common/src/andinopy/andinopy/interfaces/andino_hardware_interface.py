#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import abc


class andino_hardware_interface(abc.ABC):
    def __init__(self, broad_cast_function: callable(str)):
        self.broad_cast_function: callable(str) = broad_cast_function

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def reset(self) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def info(self) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def hardware(self, mode: int) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_polling(self, polling_time: int) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_skip(self, skip_count: int) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_edge_detection(self, value: bool) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_send_time(self, send_time: int) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_send_broadcast_timer(self, value: bool) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_debounce(self, debouncing: int) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_power(self, value: int) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_send_relays_status(self, value: bool) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_relay(self, relay_num: int, value: int) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def pulse_relay(self, relay_num: int, value: int) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_broadcast_on_change(self, value: bool) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def get_counters(self, mode: int) -> str:
        raise NotImplementedError("meta class method not overwritten")
