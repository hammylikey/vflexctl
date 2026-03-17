import pytest

from vflexctl.cli import LEDColourOption
from vflexctl.command.led import LEDColour


@pytest.mark.parametrize(["option", "expected_value"], list(zip(LEDColourOption, LEDColour)))
def test_led_option_switches_to_correct_colour(option: LEDColourOption, expected_value: LEDColour):
    assert option.to_led_colour() == expected_value
