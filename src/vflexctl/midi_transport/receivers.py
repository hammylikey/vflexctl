from time import perf_counter, sleep
from typing import cast

import structlog
from mido.ports import BaseInput

from vflexctl.types import MIDITriplet

log = structlog.get_logger("vflexctl.midi_receivers")


def drain_incoming(input_port: BaseInput, *, seconds: float = 0.5) -> list[MIDITriplet]:
    """
    "Drains" the MIDI input port for any midi messages currently available, and
    that become available over the next ``seconds`` seconds. This returns after
    the amount of seconds, whether any MIDI messages have been received or not.

    :param input_port: The MIDI input port to drain from
    :param seconds: The time to spend reading MIDI messages, in seconds.
    :return: A list of MIDI message bytes
    """
    if seconds <= 0:
        log.warning("Wait time was negative or 0 for draining incoming messages. They have not been drained.")
        return list()
    end_time = perf_counter() + seconds
    drained_bytes: list[tuple[int, int, int]] = []
    while perf_counter() <= end_time:
        drained_bytes.extend(drain_once(input_port))
        sleep(0.002)

    log.debug("Returning drained MIDI messages", drained_bytes=drained_bytes)
    return drained_bytes


def drain_once(input_port: BaseInput) -> list[tuple[int, int, int]]:
    """
    "Drains" the MIDI input port for any midi messages currently available. Once
    the pipe is empty (when BaseInput.iter_pending() returns instead of yielding)
    this returns.

    :param input_port: The MIDI input port to drain from
    :return: A list of MIDI message bytes
    """
    drained_bytes: list[tuple[int, int, int]] = []
    for message in input_port.iter_pending():
        log.debug(
            "Drained input MIDI message",
            message=message.bytes(),
            port_name=input_port.name,
            is_input=input_port.is_input,
        )
        drained_bytes.append(cast(tuple[int, int, int], tuple(message.bytes())))
    return drained_bytes
