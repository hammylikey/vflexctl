from vflexctl.protocol import VFlexProto
from vflexctl.protocol.coders import protocol_encode_millivolts
from vflexctl.types import VFlexProtoMessage


def set_voltage_command(voltage: int) -> VFlexProtoMessage:
    """
    Creates the protocol message to set the voltage to the provided value in millivolts.

    :param voltage: The voltage to set, in millivolts.
    :return: Protocol message to send to the device.
    """
    high_byte, low_byte = protocol_encode_millivolts(voltage)
    return [VFlexProto.CMD_SET_VOLTAGE, high_byte, low_byte]


def get_voltage_command() -> VFlexProtoMessage:
    """
    Creates the protocol message to get the voltage from the device, in millivolts.

    :return: Protocol message to send to the device.
    """
    return [VFlexProto.CMD_GET_VOLTAGE]
