from vflexctl.exceptions import InvalidProtocolMessageLengthError


def protocol_decode_serial_number(protocol_message: list[int]) -> str:
    if len(protocol_message) != 10:
        raise InvalidProtocolMessageLengthError(protocol_message, 10)
    return bytearray(protocol_message[2:]).decode()
