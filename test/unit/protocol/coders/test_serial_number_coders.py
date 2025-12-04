import pytest

from vflexctl.exceptions import InvalidProtocolMessageLengthError, IncorrectCommandByte
from vflexctl.protocol import VFlexProto
from vflexctl.protocol.coders import protocol_decode_serial_number

MOCK_SERIAL = "12345678"
MOCK_SERIAL_PAYLOAD = [ord(c) for c in MOCK_SERIAL]


def test_protocol_decode_serial_number_decodes_ascii_serial() -> None:
    protocol_message = [10, VFlexProto.CMD_GET_SERIAL_NUMBER, *MOCK_SERIAL_PAYLOAD]

    decoded = protocol_decode_serial_number(protocol_message)
    assert decoded == MOCK_SERIAL


def test_protocol_decode_serial_number_raises_on_invalid_length() -> None:
    protocol_message = [10, VFlexProto.CMD_GET_SERIAL_NUMBER, *MOCK_SERIAL_PAYLOAD[:-1]]

    with pytest.raises(InvalidProtocolMessageLengthError):
        protocol_decode_serial_number(protocol_message)


def test_protocol_decode_serial_number_raises_on_incorrect_command() -> None:
    protocol_message = [10, 0xFF, *MOCK_SERIAL_PAYLOAD]

    with pytest.raises(IncorrectCommandByte):
        protocol_decode_serial_number(protocol_message)
