from collections.abc import Iterable

from .logger import log


def prepare_command_frame(sub_command: Iterable[int]) -> list[int]:
    """
    Prepares a command frame for MIDI commands. Takes in an existing sub_command (like the return
    from `set_voltage_command(millivolts: int) -> list[int]`) and ensures the length is correct for it.

    :param sub_command: The subcommand to prepare for sending.
    :return: The subcommand frame prepared with its length at the start.
    """
    log.info("Preparing command frame", command=sub_command)
    sanitised_subcommand: list[int] = [int(x) for x in sub_command]
    return [
        len(sanitised_subcommand) + 1,
    ] + sanitised_subcommand
