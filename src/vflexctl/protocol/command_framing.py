from collections.abc import Iterable
from typing import cast

from . import VFlexProto
from .logger import log
from ..types import MIDITriplet, VFlexProtoMessage

__all__ = ["prepare_command_frame", "prepare_command_for_sending"]


def prepare_command_frame(sub_command: Iterable[int]) -> list[int]:
    """
    Adds the length protocol byte for the message. Takes in an existing sub_command (like the return
    from `set_voltage_command(millivolts: int) -> list[int]`) and prepends the length byte.

    :param sub_command: The subcommand to prepare for sending.
    :return: The subcommand frame prepared with its length at the start.
    """
    if isinstance(sub_command, set):
        raise TypeError(
            "sub_command is iterable, but a set is unordered. This won't process a set to guard against bad commands."
        )
    log.info("Preparing command frame", command=sub_command)
    sanitised_subcommand: list[int] = [int(x) for x in sub_command]
    return [
        len(sanitised_subcommand) + 1,
    ] + sanitised_subcommand


def midi_bytes_from_protocol_byte(protocol_byte: int) -> MIDITriplet:
    """
    Takes a protocol byte (from a VFlex protocol message) and turns it into a MIDI
    message as bytes.
    :param protocol_byte: The protocol byte to send as MIDI
    :return: The MIDI message as bytes
    """
    return (
        VFlexProto.NOTE_STATUS,
        (protocol_byte >> 4) & 0x0F,
        protocol_byte & 0x0F,
    )


def prepare_command_for_sending(frames: list[VFlexProtoMessage] | VFlexProtoMessage) -> list[MIDITriplet]:
    """
    Prepares a command to be sent by MIDI, breaking up a command
    into a list of hex triplets to be sent across by MIDI.

    :param frames: The command frame(s) to send to the device.
    :return: The list of MIDI notes/commands to send to the device.
    """
    if len(frames) == 0:
        raise ValueError("No subcommand frames provided.")
    if isinstance(frames[0], int):
        frames = [frames]

    command: list[MIDITriplet] = [VFlexProto.COMMAND_START]
    pre_transport_command: list[int] = []
    for frame in frames:
        for byte_integer in frame:
            pre_transport_command.extend(midi_bytes_from_protocol_byte(byte_integer))
    command.extend(_split_to_triplets(pre_transport_command))
    command.append(VFlexProto.COMMAND_END)
    return command


def _split_to_triplets(command: list[int]) -> list[MIDITriplet]:
    if len(command) % 3 != 0:
        raise ValueError("Command length must be multiple of 3")

    return [cast(tuple[int, int, int], tuple(command[i : i + 3])) for i in range(0, len(command), 3)]
