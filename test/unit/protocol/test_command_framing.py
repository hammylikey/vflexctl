import pytest
import mido

from vflexctl.protocol import VFlexProto
from vflexctl.protocol.command_framing import *


def test_prepare_command_frame_correctly_adds_length():
    command_frame = prepare_command_frame([VFlexProto.CMD_GET_VOLTAGE])
    # This is a one-protocol byte message, so it should have a length of 2 including itself
    assert command_frame[0] == 2


def test_prepare_command_frame_also_works_with_a_tuple_command():
    command_frame = prepare_command_frame((VFlexProto.CMD_SET_VOLTAGE, 2, 3))
    assert command_frame[0] == 4
    assert isinstance(command_frame, list)


def test_prepare_command_frame_rejects_a_set_for_safety():
    """
    This should reject sets, since the order isn't guaranteed and processing a set
    could be bad for the device.
    """
    with pytest.raises(TypeError):
        _ = prepare_command_frame({VFlexProto.CMD_GET_SERIAL_NUMBER})


def test_prepare_command_for_sending_makes_a_list_of_midi_messages():
    """
    This test fails if/when Message.from_bytes fails due to a malformed MIDI message.
    :return:
    """
    command_frame = prepare_command_frame([VFlexProto.CMD_GET_VOLTAGE])
    prepared_command = prepare_command_for_sending(command_frame)
    for midi_triplet in prepared_command:
        _ = mido.Message.from_bytes(midi_triplet)
