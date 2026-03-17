from enum import StrEnum
from functools import partial
from typing import Callable

import click
import typer
from rich import print, console

from vflexctl.command.led import LEDColour
from vflexctl.context import AppContext
from vflexctl.device_interface import VFlex
from vflexctl.input_handler.voltage_convert import decimal_normalise_voltage

__all__ = ["cli"]

cli: typer.Typer = typer.Typer(name="vflexctl", no_args_is_help=True)


VFLEX_MIDI_INTEGER_LIMIT = 65535
stderr = console.Console(stderr=True)


class LEDOption(StrEnum):
    ALWAYS_ON = "always-on"
    DISABLED_DURING_OPERATION = "disabled"

    def __bool__(self) -> bool:
        return self == LEDOption.DISABLED_DURING_OPERATION

    def __int__(self) -> int:
        return int(bool(self))


class LEDColourOption(StrEnum):
    OFF = "off"
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    WHITE = "white"
    YELLOW = "yellow"
    MAGENTA = "magenta"
    CYAN = "cyan"

    def to_led_colour(self) -> LEDColour:
        return LEDColour[self.upper()]


def _get_app_context() -> AppContext:
    obj = click.get_current_context().obj
    if not isinstance(obj, AppContext):
        raise TypeError("Context is (somehow) not of the correct type.")
    return obj


def _get_connected_v_flex(full_handshake: bool = False) -> VFlex:
    return VFlex.get_any(full_handshake=full_handshake)


def _current_state_str(v_flex: VFlex) -> str:
    message = f"""
VFlex Serial Number: {v_flex.serial_number}
Current Voltage: {float(v_flex.current_voltage or 0)/1000:.2f}
LED State: {v_flex.led_state_str}
        """.strip()
    return message


@cli.command(name="read")
def get_current_v_flex_state() -> None:
    """
    Print the current state of the connected VFlex device. (Serial, Voltage & LED setting)
    """
    context = _get_app_context()
    v_flex = _get_connected_v_flex(full_handshake=context.deep_adjust)
    v_flex.initial_wake_up()
    print(_current_state_str(v_flex))


@cli.command(name="set")
def set_v_flex_state(
    ctx: typer.Context,
    voltage: float | None = typer.Option(
        None, "--voltage", "-v", help="Voltage to set, in Volts (e.g 5.00, 12, etc, up to 48.00)"
    ),
    led: LEDOption | None = typer.Option(
        None, "--led", "-l", help='LED state to set, either "on" for always on, or "off" for not always on.'
    ),
    led_colour_option: LEDColourOption | None = typer.Option(
        None, "--led-colour", "--led-color", "--colour", "--color", help="LED colour to set."
    ),
) -> None:
    """
    Set voltage and/or LED state for the VFlex device. Prints the state after being set.
    """
    if isinstance(voltage, float | int):
        if voltage > (VFLEX_MIDI_INTEGER_LIMIT - 1 / 1000):
            stderr.print(
                "Voltage is being set higher than what can be transmitted. [bold red]The Voltage will not be set.[/bold red]"
            )
            voltage = None
        elif voltage <= 0:
            print("Voltage is being set to 0, or negative. [bold red]The Voltage will not be set.[/bold red]")
            voltage = None
    if all(x is None for x in [voltage, led, led_colour_option]):
        stderr.print(
            "[bold red]Error:[/bold red] Specify at least one of "
            "[cyan]--voltage[/cyan], [cyan]--led[/cyan], or [cyan]--led-colour[/cyan]."
        )
        print(ctx.get_help())
        raise typer.Exit(code=1)

    context = _get_app_context()
    v_flex = _get_connected_v_flex(full_handshake=context.deep_adjust)
    v_flex.initial_wake_up()
    adjustments: list[Callable[[], None]] = []
    message: list[str] = []
    if voltage is not None:
        message.append(f"Setting voltage to {decimal_normalise_voltage(voltage)}V")
        adjustments.append(partial(v_flex.set_voltage_volts, voltage))
    if led is not None:
        pre_msg = "Setting LED to "
        pre_msg += "be disabled during operation" if bool(led) else "always be on"
        message.append(pre_msg)
        adjustments.append(partial(v_flex.set_led_state, bool(led)))
    if led_colour_option is not None:
        message.append(f"Setting LED colour to {led_colour_option}")
        adjustments.append(partial(v_flex.set_led_colour, led_colour_option.to_led_colour()))
    print("\n".join(message))

    for func in adjustments:
        try:
            func()
        except Exception as e:
            v_flex.log.exception("Error when changing a setting", exc_info=e)

    print("State post set:")
    print(_current_state_str(v_flex))
    return None
