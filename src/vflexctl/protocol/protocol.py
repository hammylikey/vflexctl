from typing import Final, cast
from vflexctl.types import MIDITriplet

__all__ = ["VFlexProto", "protocol_message_from_midi_messages"]


class VFlexProto:
    """MIDI framing sentinels and transport status bytes used by the VFlex."""

    COMMAND_START: Final[MIDITriplet] = (0x80, 0, 0)
    """Start-of-frame pseudo-SYSEX marker."""

    COMMAND_END: Final[MIDITriplet] = (0xA0, 0, 0)
    """End-of-frame marker."""

    NOTE_STATUS: Final = 0x90
    """Status byte for MIDI note-on messages encoding protocol nibbles."""

    MIDI_CLOCK_HEARTBEAT: Final = (0xF8,)
    """MIDI Clock command used as a heartbeat. The website sends this every ~6 seconds."""

    CMD_GET_SERIAL_NUMBER: Final = 0x08  # 8
    """Protocol byte for the command to get the Serial Number."""

    CMD_GET_LED_STATE: Final = 0x0F  # 15
    """Protocol byte for the command to get the LED state."""

    CMD_SET_LED_STATE: Final = CMD_GET_LED_STATE | 0x80
    """Protocol byte for the command to set the LED state."""

    CMD_GET_VOLTAGE: Final = 0x12  # 18
    """Protocol byte for the command to get Voltage"""

    CMD_SET_VOLTAGE: Final = CMD_GET_VOLTAGE | 0x80
    """Protocol byte for the command to set the Voltage."""


def is_control_frame(message: MIDITriplet) -> bool:
    return message in {VFlexProto.COMMAND_START, VFlexProto.COMMAND_END}


def protocol_byte_from_midi_bytes(midi_message: MIDITriplet) -> int:
    """
    Takes a MIDI message and turns it into a protocol byte with the protocol used by
    a VFlex adapter.

    A protocol-based message from a VFlex is a collection of multiple MIDI messages,
    usually formatted as:

    [ length_of_command, command_byte (what command it is), data_1, ... ]

    This returns ONE of these protocol bytes

    :param midi_message: The MIDI message to convert to a protocol byte
    :return:
    """
    return midi_message[1] << 4 | midi_message[2]


def protocol_message_from_midi_messages(midi_messages: list[MIDITriplet]) -> list[int]:
    """
    Decode a list of received MIDI triples into a protocol message.

    The message is reconstructed from the nibbles of each MIDI NOTE_ON event
    and then validated against the protocol's self-describing length field.

    :param midi_messages: The MIDI messages to convert to a protocol message
    :return: A valid protocol message, with the correct length based on the first protocol byte.
    :raises ValueError: There aren't enough protocol bytes to satisfy the message
    :raises IndexError: There are no protocol bytes to satisfy the message
    """
    unsanitised_message: list[int] = []
    for midi_message in midi_messages:
        if is_control_frame(cast(MIDITriplet, tuple(midi_message))):
            continue
        unsanitised_message.append(protocol_byte_from_midi_bytes(midi_message))
    return validate_and_trim_protocol_message(unsanitised_message)


def validate_and_trim_protocol_message(protocol_message: list[int]) -> list[int]:
    """
    Validate a protocol message based on its self-declared length (proto[0]).

    Returns exactly the declared-length prefix.

    :param protocol_message: The protocol message to validate/trim
    :return: The trimmed protocol message
    :raises ValueError: The protocol message isn't long enough
    """
    message_length = protocol_message[0]
    if len(protocol_message) < message_length:
        raise ValueError(
            f"The protocol message provided isn't long enough. It should be at least {message_length} long."
        )
    sanitised_message: list[int] = protocol_message[:message_length]
    return sanitised_message
