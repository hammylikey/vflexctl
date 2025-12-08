from enum import StrEnum

import typer
from rich import print

from vflexctl.device_interface import VFlex

__all__ = ["cli"]

from vflexctl.input_handler.voltage_convert import decimal_normalise_voltage

cli = typer.Typer(name="vflexctl", no_args_is_help=True)

VFLEX_MIDI_INTEGER_LIMIT = 65535


class LEDOption(StrEnum):
    ALWAYS_ON = "always-on"
    DISABLED_DURING_OPERATION = "disabled"

    def __bool__(self) -> bool:
        return self == LEDOption.DISABLED_DURING_OPERATION

    def __int__(self) -> int:
        return int(bool(self))


def _get_connected_v_flex() -> VFlex:
    return VFlex.get_any()


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
    v_flex = _get_connected_v_flex()
    v_flex.wake_up()
    print(_current_state_str(v_flex))


@cli.command(name="set")
def set_v_flex_state(
    voltage: float | None = typer.Option(
        None, "--voltage", "-v", help="Voltage to set, in Volts (e.g 5.00, 12, etc, up to 48.00)"
    ),
    led: LEDOption | None = typer.Option(
        None, "--led", "-l", help='LED state to set, either "on" for always on, or "off" for not always on.'
    ),
) -> None:
    """
    Set voltage and/or LED state for the VFlex device. Prints the state after being set.
    """
    if isinstance(voltage, float | int):
        if voltage > (VFLEX_MIDI_INTEGER_LIMIT - 1 / 1000):
            print(
                "Voltage is being set higher than what can be transmitted. [bold red]The Voltage will not be set.[/bold red]"
            )
            voltage = None
        elif voltage <= 0:
            print("Voltage is being set to 0, or negative. [bold red]The Voltage will not be set.[/bold red]")
            voltage = None
    if voltage is None and led is None:
        print("[bold]You should specify either a valid voltage or LED state to set.[/bold]")
        return None
    v_flex = _get_connected_v_flex()
    v_flex.wake_up()
    message: list[str] = []
    if voltage is not None:
        message.append(f"Setting voltage to {decimal_normalise_voltage(voltage)}V")
        # message.append(f"Setting voltage to {float(voltage):.2f}V")
    if led is not None:
        pre_msg = "Setting LED to "
        pre_msg += "be disabled during operation" if bool(led) else "always be on"
        message.append(pre_msg)
    print("\n".join(message))

    if voltage is not None:
        v_flex.set_voltage_volts(voltage)
    if led is not None:
        v_flex.set_led_state(bool(led))

    print("State post set:")
    print(_current_state_str(v_flex))
    return None
