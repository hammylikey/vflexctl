import pytest

from vflexctl.input_handler.voltage_convert import voltage_to_millivolt


@pytest.mark.parametrize(["input_voltage", "expected_output_mv"], ((12, 12000), (12.0, 12000), (5, 5000), (5.5, 5500)))
def test_voltage_to_millivolt(input_voltage, expected_output_mv):
    assert voltage_to_millivolt(input_voltage) == expected_output_mv


def test_voltage_to_millivolt_can_still_work_with_string():
    """
    This is here in case the function ever receives a string representation
    of a valid number, but should be handled higher up.
    """
    assert voltage_to_millivolt("12.01") == 12010


def test_voltage_to_millivolt_raises_when_string_is_not_a_number():
    with pytest.raises(ValueError):
        voltage_to_millivolt("hello")


@pytest.mark.parametrize(
    "bad_input",
    [
        print,
        lambda x: None,
        None,
        ValueError(),
    ],
)
def test_voltage_to_millivolts_raises_when_given_non_string_int_float_values(bad_input):
    with pytest.raises(ValueError):
        voltage_to_millivolt(bad_input)
