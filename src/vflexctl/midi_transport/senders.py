from time import sleep
from datetime import datetime, timedelta

import structlog
from mido import Message
from mido.ports import BaseOutput

DEFAULT_PAUSE_LENGTH = 0.002

log = structlog.get_logger("vflexctl.midi_senders")

def send_triplet(output: BaseOutput, triplet_data: tuple[int, int, int], *, pause=0.002):
    """
    Send a single 3-byte MIDI message
    :param output: MIDI output to send the message to/through
    :param triplet_data: The 3 bytes to send
    :param pause: The amount of time to pause before returning
    :return:
    """
    message = Message.from_bytes(triplet_data)
    output.send(message)
    sleep(pause)
