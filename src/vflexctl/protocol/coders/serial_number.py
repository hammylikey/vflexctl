from vflexctl.exceptions import InvalidProtocolMessageLengthError, IncorrectCommandByte
from vflexctl.protocol import VFlexProto


def protocol_decode_serial_number(protocol_message: list[int]) -> str:
    if len(protocol_message) != 10:
        raise InvalidProtocolMessageLengthError(protocol_message, 10)
    if protocol_message[1] != VFlexProto.CMD_GET_SERIAL_NUMBER:
        raise IncorrectCommandByte(protocol_message, VFlexProto.CMD_GET_SERIAL_NUMBER)
    return bytearray(protocol_message[2:]).decode()
