from typing import Literal

from vflexctl.types import VFlexProtoMessage
from vflexctl.protocol import VFlexProto


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
