from math import floor

import structlog

__all__ = ["voltage_to_millivolt"]
log = structlog.get_logger()


def voltage_to_millivolt(voltage: float | int) -> int:
    """
    Takes in a number representing a voltage and converts it to millivolts.

    :param voltage: A float or integer for the voltage. Expects a voltage
        that goes to at most 2 decimal places, and will round a voltage provided
        that's longer than 2 decimal places.
    :return: Integer representing the voltage in millivolts.
    """
    if isinstance(voltage, str):
        try:
            voltage = float(voltage)
        except ValueError as e:
            log.exception("Got a value that cannot be converted to a number.", exc_info=e)
            raise
    if not isinstance(voltage, float | int):
        exc = TypeError("This function only accepts numbers.")
        log.exception(
            "Got an invalid value. By this line, the value should be a float or int",
            exc=exc,
            value=voltage,
            value_type=type(voltage).__name__,
        )
        raise exc
    rounded_voltage: float = round(float(voltage), 2)
    return int(floor(rounded_voltage * 1000))
