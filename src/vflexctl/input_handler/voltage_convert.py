from math import floor

__all__ = ["voltage_to_millivolt"]


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
        except ValueError:
            print("Got a value that cannot be converted to millivolts.")
    if not isinstance(voltage, float | int):
        raise TypeError("This function only accepts numbers.")
    rounded_voltage: float = round(float(voltage), 2)
    return int(floor(rounded_voltage * 1000))
