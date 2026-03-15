from vflexctl.exceptions import InvalidProtocolMessageLengthError, IncorrectCommandByte
from vflexctl.protocol import VFlexProto

__all__ = [
    "protocol_decode_serial_number",
    "protocol_decode_hardware_revision",
    "protocol_decode_firmware_version",
]


def protocol_decode_serial_number(protocol_message: list[int]) -> str:
    if len(protocol_message) != 10:
        raise InvalidProtocolMessageLengthError(protocol_message, 10)
    if protocol_message[1] != VFlexProto.CMD_GET_SERIAL_NUMBER:
        raise IncorrectCommandByte(protocol_message, VFlexProto.CMD_GET_SERIAL_NUMBER)
    return bytearray(protocol_message[2:]).decode()


def protocol_decode_hardware_revision(protocol_message: list[int]) -> str:
    if protocol_message[1] != VFlexProto.CMD_GET_HARDWARE_REVISION:
        raise IncorrectCommandByte(protocol_message, VFlexProto.CMD_GET_HARDWARE_REVISION)
    return bytearray(protocol_message[2:]).decode()


def protocol_decode_firmware_version(protocol_message: list[int]) -> str:
    if len(protocol_message) != 14:
        raise InvalidProtocolMessageLengthError(protocol_message, 14)
    if protocol_message[1] != VFlexProto.CMD_GET_FIRMWARE_VERSION:
        raise IncorrectCommandByte(protocol_message, VFlexProto.CMD_GET_FIRMWARE_VERSION)
    return bytearray(protocol_message[2:]).decode()
