import pytest

from vflexctl.exceptions import InvalidProtocolMessageLengthError, IncorrectCommandByte
from vflexctl.protocol import VFlexProto
from vflexctl.protocol.coders import (
    get_millivolts_from_protocol_message,
    protocol_encode_millivolts,
    protocol_decode_millivolts,
)


@pytest.fixture
def mock_protocol_bytes_return():
    yield [4, VFlexProto.CMD_GET_VOLTAGE, 19, 136]


def test_get_millivolts_from_protocol_message_gets_millivolts(mock_protocol_bytes_return):
    mv = get_millivolts_from_protocol_message(mock_protocol_bytes_return)
    assert mv == 5000


def test_get_millivolts_from_protocol_message_raises_when_message_is_too_short():
    with pytest.raises(InvalidProtocolMessageLengthError):
        _ = get_millivolts_from_protocol_message([1, 2])


def test_get_millivolts_from_protocol_message_raises_when_message_is_too_long():
    with pytest.raises(InvalidProtocolMessageLengthError):
        _ = get_millivolts_from_protocol_message([1, 2, 3, 4, 5])


def test_get_millivolts_from_protocol_message_raises_if_command_is_not_correct():
    with pytest.raises(IncorrectCommandByte):
        _ = get_millivolts_from_protocol_message([4, VFlexProto.CMD_GET_VOLTAGE - 1, 16, 32])


@pytest.mark.parametrize(
    "millivolts",
    [
        5000,
        12000,
        12500,
        15000,
        48000,
    ],
)
def test_protocol_encode_and_decode_millivolts_are_paired(millivolts):
    encoded_mv = protocol_encode_millivolts(millivolts)
    assert millivolts == encoded_mv[0] << 8 | encoded_mv[1]
    decoded_mv = protocol_decode_millivolts(encoded_mv[0], encoded_mv[1])
    assert decoded_mv == millivolts
