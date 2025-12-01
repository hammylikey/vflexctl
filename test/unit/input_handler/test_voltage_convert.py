import pytest
from vflexctl.input_handler.voltage_convert import voltage_to_millivolt, millivolt_to_high_low_ints


@pytest.mark.parametrize(["input_voltage", "expected_output_mv"], ((12, 12000), (12.0, 12000), (5, 5000), (5.5, 5500)))
def test_voltage_to_millivolt(input_voltage, expected_output_mv):
    assert voltage_to_millivolt(input_voltage) == expected_output_mv


def test_voltage_to_millivolt_can_still_work_with_string():
    """
    This is here in case the function ever receives a string representation
    of a valid number, but should be handled higher up.
    """
    assert voltage_to_millivolt("12.01") == 12010


def test_millivolt_to_high_low_int_works():
    expected_mv = 5000
    high_byte, low_byte = millivolt_to_high_low_ints(expected_mv)
    assert (high_byte << 8) + low_byte == expected_mv
