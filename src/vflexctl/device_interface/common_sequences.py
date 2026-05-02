"""
Common commands, into a list of MIDI notes. These are here so that they don't need to be
made with command_preparation.
"""

from vflexctl.protocol import VFlexProto, prepare_command_for_sending, prepare_command_frame
from vflexctl.types import MIDITriplet

__all__ = ["GET_VOLTAGE_SEQUENCE", "GET_LED_STATE_SEQUENCE", "GET_SERIAL_NUMBER_SEQUENCE"]


type CommandList = list[
    MIDITriplet
]  # Already prepared command, good for sending, vs a VFlexProtoMessage which needs preparation

GET_SERIAL_NUMBER_SEQUENCE: CommandList = prepare_command_for_sending(
    prepare_command_frame([VFlexProto.CMD_GET_SERIAL_NUMBER])
)

GET_LED_STATE_SEQUENCE: CommandList = prepare_command_for_sending(prepare_command_frame([VFlexProto.CMD_GET_LED_STATE]))

GET_VOLTAGE_SEQUENCE: CommandList = prepare_command_for_sending(prepare_command_frame([VFlexProto.CMD_GET_VOLTAGE]))
