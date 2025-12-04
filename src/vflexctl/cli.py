from typing import Literal

import typer

from vflexctl.device_interface import VFlex

__all__ = ["cli"]

cli = typer.Typer(name="vflexctl", no_args_is_help=True)

type LEDOption = Literal["on", "off"]


def _get_connected_v_flex() -> VFlex:
    return VFlex.get_any()


def _print_current_state(v_flex: VFlex):
    message = f"""
VFlex Serial Number: {v_flex.serial_number}
Current Voltage: {float(v_flex.current_voltage)/1000:.2f}
LED State: {v_flex.led_state_str}
        """.strip()
    typer.echo(message)


@cli.command(name="read")
def get_current_v_flex_state() -> None:
    """
    Print the current state of the connected VFlex device. (Serial, Voltage & LED setting)
    """
    v_flex = _get_connected_v_flex()
    v_flex.wake_up()
    _print_current_state(v_flex)


@cli.command(name="set")
def set_v_flex_state(
    voltage: float | None = typer.Option(
        None, "--voltage", "-v", help="Voltage to set, in Volts (e.g 5.00, 12, etc, up to 48.00)"
    ),
    led: Literal["on", "off"] | None = typer.Option(
        None, "--led", "-l", help='LED state to set, either "on" for always on, or "off" for not always on.'
    ),
):
    """
    Set voltage and/or LED state for the VFlex device. Prints the state after being set.
    """
    if voltage is None and led is None:
        print("You should specify either a voltage or LED state to set.")
        return None
    v_flex = _get_connected_v_flex()
    v_flex.wake_up()
    message: list[str] = []
    if voltage is not None:
        message.append(f"Setting voltage to {float(voltage):.2f}V")
    if led is not None:
        pre_msg = "Setting LED to "
        if led == "on":
            pre_msg += "be always on"
        else:
            pre_msg += "not be always on"
        message.append(pre_msg)
    typer.echo("\n".join(message))

    if voltage is not None:
        v_flex.set_voltage_volts(voltage)
    if led is not None:
        v_flex.set_led_state(0 if led == "on" else 1)

    typer.echo("State post set:")
    _print_current_state(v_flex)
    return None
