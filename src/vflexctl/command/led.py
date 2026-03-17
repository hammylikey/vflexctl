from enum import IntEnum
from typing import Literal

from vflexctl.types import VFlexProtoMessage
from vflexctl.protocol import VFlexProto


class LEDColour(IntEnum):
    """Enumeration for the LED colour mode."""

    OFF = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    WHITE = 4
    YELLOW = 5
    MAGENTA = 6
    CYAN = 7


def set_led_state_command(value: bool | Literal[0, 1]) -> VFlexProtoMessage:
    """
    Creates the protocol message to set the LED state to the provided value. In this context:

    - False, 0: LED is always on (0x00, default behaviour).
    - True, 1: LED is not always on (0x01, customised behaviour).

    :param value: The value to set the LED state to.
    :return: Protocol message to send to the device.
    """
    int_value = int(value)
    return [VFlexProto.CMD_SET_LED_STATE, int_value]


def set_led_colour_command(colour: LEDColour) -> VFlexProtoMessage:
    """
    Creates the protocol message to set the LED colour to the provided value.

    :param colour: The colour to set the LED to.
    :return: Protocol message to send to the device.
    """
    return [VFlexProto.CMD_SET_LED_COLOUR, 10, 1, colour, 2, 0]
