from collections.abc import Callable
from functools import wraps
from typing import Any, Self
from typing import Literal

import mido
import structlog
from mido.ports import BaseIOPort

from vflexctl.command.led import set_led_state_command
from vflexctl.command.voltage import set_voltage_command
from vflexctl.device_interface import (
    prepare_command_for_sending,
    GET_LED_STATE_SEQUENCE,
    GET_VOLTAGE_SEQUENCE,
    GET_SERIAL_NUMBER_SEQUENCE,
)
from vflexctl.exceptions import InvalidProtocolMessageLengthError, SerialNumberMismatchError
from vflexctl.midi_transport.receivers import drain_incoming
from vflexctl.midi_transport.senders import send_sequence
from vflexctl.protocol import protocol_message_from_midi_messages, prepare_command_frame
from vflexctl.protocol.coders import (
    get_millivolts_from_protocol_message,
    protocol_decode_led_state,
    protocol_decode_serial_number,
)

DEFAULT_PORT_NAME = "Werewolf vFlex"

__all__ = ["VFlex"]


def run_with_handshake(func: Callable[..., Any]):

    @wraps(func)
    def wrapper(v_flex: "VFlex", *args: Any, **kwargs: Any) -> Any:
        v_flex.log.info("Running wake-up commands")
        v_flex.wake_up()
        return func(v_flex, *args, **kwargs)

    return wrapper


class VFlex:
    """High-level interface for communicating with a VFlex MIDI power adapter."""

    # The underlying MIDI I/O port used for sending and receiving messages.
    io_port: BaseIOPort

    # Structured logger bound to this specific VFlex instance.
    log: structlog.BoundLogger

    # Cached serial number of the device (None until fetched).
    serial_number: str | None = None

    # Last known voltage in millivolts, retrieved from the device.
    current_voltage: int | None = None

    # LED behaviour state as reported by the device.
    led_state: int | None = None

    # Whether to enforce safety checks (e.g., ensuring serial number doesn't change).
    safe_adjust: bool

    def __init__(self, io_port: BaseIOPort, safe_adjust: bool = True):
        self.io_port = io_port
        self.log = structlog.get_logger("vflexctl.VFlex").bind(io_port=io_port)
        self.safe_adjust = safe_adjust

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

    def wake_up(self) -> None:
        """
        "Wakes up" the connected VFlex to get it ready to receive commands. Functions
        that use the `run_with_handshake()` decorator automatically use htis

        :return: Nothing, but ensures that the device is ready to receive commands.
        """
        self.get_serial_number()
        self._initial_get_voltage()

    def get_serial_number(self) -> None:
        """
        Fetches (or re-fetches) the serial number of the connected VFlex.

        :return: Nothing, but adds the serial number to the class if it's not there.
        :raises SerialNumberMismatchError: The serial number has changed between fetches.
        """
        send_sequence(self.io_port, GET_SERIAL_NUMBER_SEQUENCE)
        returned_data = drain_incoming(self.io_port)
        try:
            returned_serial_number = protocol_decode_serial_number(protocol_message_from_midi_messages(returned_data))
        except InvalidProtocolMessageLengthError as e:
            self.log.exception("Failed to decode serial number.", exc_info=e)
            if self.safe_adjust:
                raise e
            return None

        if self.serial_number is None or not self.safe_adjust:
            self.serial_number = returned_serial_number
        if self.safe_adjust and self.serial_number != returned_serial_number:
            raise SerialNumberMismatchError(
                old_serial_number=self.serial_number, new_serial_number=returned_serial_number
            )
        return None

    def _initial_get_voltage(self) -> None:
        """
        Initial get voltage command. This is used to wake the device up in wake_up. To actually get voltage, you
        likely want to use `get_voltage()`. Instead.

        :return: Nothing, but adds the initial voltage into the object.
        """
        send_sequence(self.io_port, GET_VOLTAGE_SEQUENCE)
        returned_data = drain_incoming(self.io_port)
        self.current_voltage = get_millivolts_from_protocol_message(protocol_message_from_midi_messages(returned_data))

    def _initial_get_led_state(self) -> None:
        send_sequence(self.io_port, GET_LED_STATE_SEQUENCE)
        returned_data = drain_incoming(self.io_port)
        self.led_state = protocol_decode_led_state(protocol_message_from_midi_messages(returned_data))

    @run_with_handshake
    def get_voltage(self) -> int:
        """
        Runs the "Get Voltage" command on device to get the voltage. This both returns the value and adds it to
        the object under `self.current_voltage`.

        :return: Integer for the current voltage, in millivolts. (Float divide by 1000 to get the Volts)
        """
        send_sequence(self.io_port, GET_VOLTAGE_SEQUENCE)
        returned_data = drain_incoming(self.io_port)
        millivolts = get_millivolts_from_protocol_message(protocol_message_from_midi_messages(returned_data))
        self.current_voltage = millivolts
        return millivolts

    @run_with_handshake
    def set_voltage(self, volts: int) -> None:
        command = prepare_command_for_sending(prepare_command_frame(set_voltage_command(volts)))
        send_sequence(self.io_port, command)
        returned_data = drain_incoming(self.io_port)
        returned_voltage = get_millivolts_from_protocol_message(protocol_message_from_midi_messages(returned_data))
        self.log.debug("Voltage returned after setting", returned_voltage=returned_voltage)
        self.current_voltage = returned_voltage

    @run_with_handshake
    def set_led_state(self, led_state: bool | Literal[0, 1]) -> None:
        command = prepare_command_for_sending(prepare_command_frame(set_led_state_command(led_state)))
        send_sequence(self.io_port, command)
        returned_data = drain_incoming(self.io_port)
        send_sequence(self.io_port, GET_LED_STATE_SEQUENCE)
        self.led_state = protocol_decode_led_state(protocol_message_from_midi_messages(returned_data))
