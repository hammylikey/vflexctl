import pytest

from vflexctl.protocol.protocol import (
    VFlexProto,
    protocol_message_from_midi_messages,
    validate_and_trim_protocol_message,
)
from vflexctl.protocol.command_framing import midi_bytes_from_protocol_byte
from vflexctl.types import MIDITriplet


def test_protocol_message_from_midi_messages_happy_path() -> None:
    # Example: [length, cmd, payload0, payload1]
    proto_bytes = [
        4,
        VFlexProto.CMD_GET_VOLTAGE,
        0x2E,
        0xE0,
    ]

    midi_messages: list[MIDITriplet] = [VFlexProto.COMMAND_START]
    midi_messages.extend(midi_bytes_from_protocol_byte(b) for b in proto_bytes)
    midi_messages.append(VFlexProto.COMMAND_END)

    result = protocol_message_from_midi_messages(midi_messages)

    assert result == proto_bytes


def test_protocol_message_from_midi_messages_ignores_control_frames() -> None:
    proto_bytes = [2, VFlexProto.CMD_GET_SERIAL_NUMBER]

    midi_messages: list[MIDITriplet] = [
        VFlexProto.COMMAND_START,
        midi_bytes_from_protocol_byte(proto_bytes[0]),
        midi_bytes_from_protocol_byte(proto_bytes[1]),
        VFlexProto.COMMAND_END,
    ]

    result = protocol_message_from_midi_messages(midi_messages)

    assert result == proto_bytes


def test_protocol_message_from_midi_messages_raises_on_too_short() -> None:
    """If the reconstructed protocol message is shorter than its declared length, raise ValueError."""
    proto_bytes = [
        4,
        VFlexProto.CMD_GET_VOLTAGE,
        0x2E,
    ]

    midi_messages: list[MIDITriplet] = [VFlexProto.COMMAND_START]
    midi_messages.extend(midi_bytes_from_protocol_byte(b) for b in proto_bytes)
    midi_messages.append(VFlexProto.COMMAND_END)

    with pytest.raises(ValueError):
        protocol_message_from_midi_messages(midi_messages)


def test_validate_and_trim_protocol_message_trims_extra_bytes() -> None:
    """validate_and_trim_protocol_message should return exactly the declared prefix even if extra bytes exist."""
    message = [4, VFlexProto.CMD_GET_VOLTAGE, 0x2E, 0xE0, 0xFF]

    trimmed = validate_and_trim_protocol_message(message)

    assert trimmed == [4, VFlexProto.CMD_GET_VOLTAGE, 0x2E, 0xE0]


def test_validate_and_trim_protocol_message_raises_when_too_short() -> None:
    message = [4, VFlexProto.CMD_GET_VOLTAGE, 0x2E]

    with pytest.raises(ValueError):
        validate_and_trim_protocol_message(message)
