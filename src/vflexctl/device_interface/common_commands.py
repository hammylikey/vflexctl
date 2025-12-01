"""
Common commands, into a list of MIDI notes. These are here so that they don't need to be
made with command_preparation.
"""

from vflexctl.protocol.command_framing import prepare_command_frame
from vflexctl.device_interface.command_preparation import prepare_command_for_sending

type CommandList = list[tuple[int, int, int]]

GET_SERIAL_NUMBER_COMMAND = 8
GET_LED_STATE_COMMAND = 15
GET_VOLTAGE_COMMAND = 18

GET_SERIAL_NUMBER_SEQUENCE: CommandList = prepare_command_for_sending(
    prepare_command_frame([GET_SERIAL_NUMBER_COMMAND])
)

GET_LED_STATE_SEQUENCE: CommandList = prepare_command_for_sending(prepare_command_frame([GET_LED_STATE_COMMAND]))

GET_VOLTAGE_SEQUENCE: CommandList = prepare_command_for_sending(prepare_command_frame([GET_VOLTAGE_COMMAND]))
