import pytest

from vflexctl.exceptions import InvalidProtocolMessageLengthError, IncorrectCommandByte
from vflexctl.protocol import VFlexProto
from vflexctl.protocol.coders import protocol_decode_led_state


@pytest.mark.parametrize(("led_state", "expected_bool"), [(0, False), (1, True)])
def test_protocol_decode_led_state_correctly_reads_state(led_state, expected_bool):
    protocol_msg = [3, VFlexProto.CMD_GET_LED_STATE, led_state]
    assert protocol_decode_led_state(protocol_msg) == expected_bool


def test_protocol_decode_led_state_raises_on_invalid_length():
    with pytest.raises(InvalidProtocolMessageLengthError):
        _ = protocol_decode_led_state([2, VFlexProto.CMD_GET_LED_STATE])


def test_protocol_decode_led_state_raises_on_incorrect_command():
    with pytest.raises(IncorrectCommandByte):
        _ = protocol_decode_led_state([2, VFlexProto.CMD_GET_LED_STATE - 1, 1])
