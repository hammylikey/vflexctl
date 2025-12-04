"""
Common commands, into a list of MIDI notes. These are here so that they don't need to be
made with command_preparation.
"""

from vflexctl.protocol import VFlexProto, prepare_command_for_sending, prepare_command_frame

__all__ = ["GET_VOLTAGE_SEQUENCE", "GET_LED_STATE_SEQUENCE", "GET_SERIAL_NUMBER_SEQUENCE"]

type CommandList = list[tuple[int, int, int]]

GET_SERIAL_NUMBER_SEQUENCE: CommandList = prepare_command_for_sending(
    prepare_command_frame([VFlexProto.CMD_GET_SERIAL_NUMBER])
)

GET_LED_STATE_SEQUENCE: CommandList = prepare_command_for_sending(prepare_command_frame([VFlexProto.CMD_GET_LED_STATE]))

GET_VOLTAGE_SEQUENCE: CommandList = prepare_command_for_sending(prepare_command_frame([VFlexProto.CMD_GET_VOLTAGE]))
