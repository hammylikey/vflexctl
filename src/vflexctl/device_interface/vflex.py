from functools import wraps
from collections.abc import Callable
from typing import Any, Self
import mido
from mido.ports import BaseInput, BaseOutput, BaseIOPort

__all__ = []

DEFAULT_PORT_NAME = "Werewolf vFLEX"

def run_with_handshake(func: Callable[[...], Any]):

    @wraps(func)
    def wrapper(v_flex: "VFlex", *args: Any, **kwargs: Any) -> Any:
        print("Running wake-up commands")


class VFlex:
    io_port: BaseIOPort
    serial_number: str | None = None
    current_voltage: int | None = None # Current voltage in mV
    led_state: int | None = None

    def __init__(self, io_port: BaseIOPort):
        self.io_port = io_port

    @classmethod
    def with_io_name(cls, name: str) -> Self:
        """
        Gets a handle to a VFlex adapter using a provided port name.
        :param name: The port name to use with MIDO to get the MIDI port.
        :return: VFlex instance with the correct port for talking to it.
        """
        io_names = mido.get_ioport_names()
        if name not in io_names:
            raise RuntimeError(f"I/O port name '{name}' not found.")
        return cls(mido.open_ioport(name))

    @classmethod
    def get_any(cls) -> Self:
        """
        Gets _a_ handle to a VFlex adapter using the expected port name. If multiple are connected
        there's no guarantee that multiple runs of the tool will connect to the same one.
        :return:
        """
        return cls(mido.open_ioport(DEFAULT_PORT_NAME))

    def wake_up(self) -> Self:
        ...

    @run_with_handshake
    def set_voltage(self, volts: float | int) -> None:
        ...




