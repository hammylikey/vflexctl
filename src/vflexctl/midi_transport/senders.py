from time import sleep

import structlog
from mido import Message
from mido.ports import BaseOutput

from vflexctl.types import MIDITriplet

DEFAULT_PAUSE_LENGTH = 0.002

log = structlog.get_logger("vflexctl.midi_senders")


def send_sequence(output: BaseOutput, sequence: list[MIDITriplet]) -> None:
    """
    Send a sequence of MIDI messages to a VFlex adapter. Used to run a command
    after it's been converted from the protocol into a list of MIDI messages.

    :param output: MIDI output to send the message to/through
    :param sequence: The sequence of MIDI messages to send
    :return:
    """
    log.info("Sending MIDI Sequence", sequence=sequence)
    for command in sequence:
        send_triplet(output, command)


def send_triplet(output: BaseOutput, triplet_data: MIDITriplet, *, pause: float = 0.002) -> None:
    """
    Send a single 3-byte MIDI message
    :param output: MIDI output to send the message to/through
    :param triplet_data: The 3 bytes to send
    :param pause: The amount of time to pause before returning
    :return:
    """
    message = Message.from_bytes(triplet_data)
    log.debug("Sending MIDI message", message=message.bytes(), port_name=output.name, is_output=output.is_output)
    output.send(message)
    sleep(pause)
