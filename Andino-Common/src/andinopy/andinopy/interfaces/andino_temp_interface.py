#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
import abc


class andino_temp_interface(abc.ABC):

    @abc.abstractmethod
    def set_temp_broadcast_timer(self, value: int) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def get_temp(self) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def set_bus(self, count: int) -> str:
        raise NotImplementedError("meta class method not overwritten")

    @abc.abstractmethod
    def get_addresses(self) -> str:
        raise NotImplementedError("meta class method not overwritten")
