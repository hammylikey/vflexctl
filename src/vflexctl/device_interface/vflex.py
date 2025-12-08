from collections.abc import Callable
from functools import wraps
from typing import Any, Self, TypeVar, ParamSpec, Concatenate, cast
from typing import Literal

import mido
import structlog
from mido.ports import BaseIOPort

from vflexctl.command.led import set_led_state_command
from vflexctl.command.voltage import set_voltage_command
from vflexctl.device_interface.common_sequences import (
    GET_LED_STATE_SEQUENCE,
    GET_VOLTAGE_SEQUENCE,
    GET_SERIAL_NUMBER_SEQUENCE,
)
from vflexctl.exceptions import InvalidProtocolMessageLengthError, SerialNumberMismatchError, VoltageMismatchError
from vflexctl.input_handler.voltage_convert import voltage_to_millivolt
from vflexctl.midi_transport.receivers import drain_incoming
from vflexctl.midi_transport.senders import send_sequence
from vflexctl.protocol import protocol_message_from_midi_messages, prepare_command_frame, prepare_command_for_sending
from vflexctl.protocol.coders import (
    get_millivolts_from_protocol_message,
    protocol_decode_led_state,
    protocol_decode_serial_number,
)

DEFAULT_PORT_NAME = "Werewolf vFlex"

__all__ = ["VFlex"]


P = ParamSpec("P")
R = TypeVar("R")


def run_with_handshake(func: Callable[Concatenate["VFlex", P], R]) -> Callable[Concatenate["VFlex", P], R]:

    @wraps(func)
    def wrapper(v_flex: "VFlex", *args: P.args, **kwargs: P.kwargs) -> R:
        v_flex.log.info("Running wake-up commands")
        v_flex.wake_up()
        return func(v_flex, *args, **kwargs)

    return cast(Callable[Concatenate["VFlex", P], R], wrapper)


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
    led_state: bool | None = None

    # Whether to enforce safety checks (e.g., ensuring serial number doesn't change).
    safe_adjust: bool

    def __init__(self, io_port: BaseIOPort, safe_adjust: bool = True):
        self.io_port = io_port
        self.log = structlog.get_logger("vflexctl.VFlex").bind(io_port=io_port)
        self.safe_adjust = safe_adjust

    @classmethod
    def with_io_name(cls, name: str, *, safe_adjust: bool = True) -> Self:
        """
        Gets a handle to a VFlex adapter using a provided port name.
        :param name: The port name to use with MIDO to get the MIDI port.
        :param safe_adjust: Whether (or not) to add extra checks for adjustments.
        :return: VFlex instance with the correct port for talking to it.
        """
        io_names = mido.get_ioport_names()
        if name not in io_names:
            raise RuntimeError(f"I/O port name '{name}' not found.")
        return cls(mido.open_ioport(name), safe_adjust=safe_adjust)

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
        self._initial_get_led_state()
        self._initial_get_voltage()

    def get_serial_number(self) -> str | None:
        """
        Fetches (or re-fetches) the serial number of the connected VFlex. If the object is set to `safe_adjust`,
        if the serial number changes between fetches, this **will** raise a SerialNumberMismatchError. This is
        as a safety mechanism to make sure the same VFlex is still being connected to.

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
        return returned_serial_number

    def _initial_get_voltage(self) -> None:
        """
        Initial get voltage command. This is used to wake the device up in wake_up. To actually get voltage, you
        likely want to use `get_voltage()`. Instead.

        :return: Nothing, but adds the initial voltage into the object.
        """
        send_sequence(self.io_port, GET_VOLTAGE_SEQUENCE)
        returned_data = drain_incoming(self.io_port)
        if self.current_voltage is None:
            self.current_voltage = get_millivolts_from_protocol_message(
                protocol_message_from_midi_messages(returned_data)
            )
        return None

    def _initial_get_led_state(self) -> None:
        """
        Initial get LED state command. This is used to wake the device up in wake_up. To actually get LED state, you
        likely want to use `get_led_state()`. Instead.
        :return:
        """
        send_sequence(self.io_port, GET_LED_STATE_SEQUENCE)
        returned_data = drain_incoming(self.io_port)
        if self.led_state is None:
            self.led_state = protocol_decode_led_state(protocol_message_from_midi_messages(returned_data))
        return None

    @run_with_handshake
    def get_voltage(self, *, update_self: bool = True) -> int:
        """
        Runs the "Get Voltage" command on device to get the voltage. This both returns the value, It also adds it to
        the object under `self.current_voltage` if update_self is True.

        :param update_self: On retrieving the voltage, whether to update `self.current_voltage` or not. Defaults to True.
        :return: Integer for the current voltage, in millivolts. (Float divide by 1000 to get the Volts)
        """
        send_sequence(self.io_port, GET_VOLTAGE_SEQUENCE)
        returned_data = drain_incoming(self.io_port)
        millivolts = get_millivolts_from_protocol_message(protocol_message_from_midi_messages(returned_data))
        self.log.debug("Retrieved current voltage", current_voltage=self.current_voltage)
        if update_self:
            self.current_voltage = millivolts
        return millivolts

    @run_with_handshake
    def get_led_state(self) -> bool:
        """
        Runs the "Get Led State" command on device to get the LED state. This both returns the value and adds it
        to the object under `self.led_state`.

        :return:
        """
        send_sequence(self.io_port, GET_LED_STATE_SEQUENCE)
        returned_data = drain_incoming(self.io_port)
        led_state = protocol_decode_led_state(protocol_message_from_midi_messages(returned_data))
        self.log.debug("Retrieved LED State", led_state=led_state)
        self.led_state = led_state
        return led_state

    @run_with_handshake
    def set_voltage(self, millivolts: int) -> None:
        """
        Set the voltage for the device to the specified number of millivolts. Updates the current voltage
        with the data returned after the command.

        The VFlex *should* return the new voltage, but if you wanted to be safer, run get_voltage() again
        after this.

        :param millivolts: The voltage to set the device to, in millivolts.
        :return: Nothing, but updates the voltage for the object under self.current_voltage.
        """
        self._guard_voltage()
        command = prepare_command_for_sending(prepare_command_frame(set_voltage_command(millivolts)))
        send_sequence(self.io_port, command)
        returned_data = drain_incoming(self.io_port)
        returned_voltage = get_millivolts_from_protocol_message(protocol_message_from_midi_messages(returned_data))
        self.log.debug("Voltage returned after setting", returned_voltage=returned_voltage)
        self.current_voltage = returned_voltage

    def set_voltage_volts(self, volts: float) -> None:
        """
        Set the voltage for the device to the specified number of volts. Converts to millivonts
        before calling set_voltage().
        :param volts: The voltage to set the device to, in volts.
        :return: Nothing, but updates the voltage for the object under self.current_voltage.
        """
        self.set_voltage(millivolts=voltage_to_millivolt(volts))

    @run_with_handshake
    def set_led_state(self, led_state: bool | Literal[0, 1]) -> None:
        """
        Set the LED state for the device to the specified LED state. Updates the current LED state
        with the data returned after the command.

        The LED states are defined as:

        - False, 0: LED is always on (0x00, default behaviour).
        - True, 1: LED is not always on (0x01, customised behaviour).

        :param led_state: The LED state to set the device to.
        :return: Nothing, but updates the LED state for the object under self.current_led_state.
        """
        command = prepare_command_for_sending(prepare_command_frame(set_led_state_command(led_state)))
        send_sequence(self.io_port, command)
        _ = drain_incoming(self.io_port)
        send_sequence(self.io_port, GET_LED_STATE_SEQUENCE)
        returned_data = drain_incoming(self.io_port)
        self.led_state = protocol_decode_led_state(protocol_message_from_midi_messages(returned_data))
        self.log.debug("LED State returned after setting", led_state=self.led_state)

    @run_with_handshake
    def _guard_voltage(self) -> None:
        """
        Guards against the voltage changing if self.safe_adjust is True.
        :return: Nothing
        :raises VoltageMismatchError: Subclass of UnsafeAdjustmentError, if the voltage stored does not match
        the voltage that's re-retrieved.
        """
        if not self.safe_adjust:
            return None
        reported_current_voltage = self.get_voltage(update_self=False)
        if reported_current_voltage != self.current_voltage:
            raise VoltageMismatchError(stored_voltage=self.current_voltage, retrieved_voltage=reported_current_voltage)
        return None

    @property
    def led_state_str(self) -> str:
        return "always on" if self.led_state is False else "disabled during operation"
