import pytest

from vflexctl.device_interface import VFlex
from vflexctl.exceptions import (
    VoltageMismatchError,
    SerialNumberMismatchError,
    InvalidProtocolMessageLengthError,
)


@pytest.fixture
def mock_io_port(mocker):
    yield mocker.MagicMock(name="mock_io_port")


@pytest.fixture
def mock_protocol_message_from_midi_messages(mocker):
    yield mocker.patch("vflexctl.device_interface.vflex.protocol_message_from_midi_messages")


@pytest.mark.parametrize("wake_up_commands", ["get_voltage", "get_led_state"])
def test_v_flex_runs_wakeup_with_expected_members(mock_io_port, wake_up_commands, mocker):
    """
    This tests that the decorator is calling wake_up correctly before commands.
    """
    mocker.patch("vflexctl.device_interface.vflex.protocol_message_from_midi_messages")
    mocker.patch("vflexctl.device_interface.vflex.drain_incoming")
    mocker.patch("vflexctl.device_interface.vflex.protocol_decode_serial_number", return_value="fooSerial")
    mocker.patch("vflexctl.device_interface.vflex.get_millivolts_from_protocol_message", return_value=5000)
    mocker.patch("vflexctl.device_interface.vflex.protocol_decode_led_state", return_value=False)
    v_flex = VFlex(mock_io_port, safe_adjust=False)
    v_flex.wake_up = mocker.MagicMock(name="wake_up")
    getattr(v_flex, wake_up_commands, lambda: None)()
    v_flex.wake_up.assert_called_once()


def test_v_flex_initialises_with_wake_up_as_expected(mocker, mock_io_port):
    mocker.patch("vflexctl.device_interface.vflex.protocol_message_from_midi_messages")
    mocker.patch("vflexctl.device_interface.vflex.drain_incoming")
    mocker.patch("vflexctl.device_interface.vflex.protocol_decode_serial_number", return_value="fooSerial")
    mocker.patch("vflexctl.device_interface.vflex.get_millivolts_from_protocol_message", return_value=5000)
    mocker.patch("vflexctl.device_interface.vflex.protocol_decode_led_state", return_value=False)
    v_flex = VFlex(mock_io_port, safe_adjust=False)
    v_flex.wake_up()
    assert v_flex.current_voltage == 5000
    assert v_flex.led_state == False
    assert v_flex.serial_number == "fooSerial"


def test_safe_adjust_guards_on_serial_number_changing(mocker, mock_io_port, mock_protocol_message_from_midi_messages):
    mocker.patch("vflexctl.device_interface.vflex.drain_incoming")
    mock_serial = mocker.patch(
        "vflexctl.device_interface.vflex.protocol_decode_serial_number", return_value="fooSerial"
    )
    mocker.patch("vflexctl.device_interface.vflex.get_millivolts_from_protocol_message", return_value=5000)
    mocker.patch("vflexctl.device_interface.vflex.protocol_decode_led_state", return_value=False)
    v_flex = VFlex(mock_io_port, safe_adjust=True)
    v_flex.wake_up()
    assert v_flex.serial_number == "fooSerial"
    mock_serial.return_value = "fooSerialAgain"
    with pytest.raises(SerialNumberMismatchError):
        v_flex.set_voltage(5000)


def test_safe_adjust_stops_allowing_adjustment_if_we_dont_get_the_serial(
    mocker, mock_io_port, mock_protocol_message_from_midi_messages
):
    mocker.patch("vflexctl.device_interface.vflex.drain_incoming")
    mocker.patch(
        "vflexctl.device_interface.vflex.protocol_decode_serial_number",
        side_effect=InvalidProtocolMessageLengthError([], 10),
    )
    mocker.patch("vflexctl.device_interface.vflex.get_millivolts_from_protocol_message", return_value=5000)
    mocker.patch("vflexctl.device_interface.vflex.protocol_decode_led_state", return_value=False)
    with pytest.raises(InvalidProtocolMessageLengthError):
        v_flex = VFlex(mock_io_port, safe_adjust=True)
        v_flex.wake_up()


def test_set_voltage_guards_as_standard_if_the_voltage_changes(
    mocker, mock_io_port, mock_protocol_message_from_midi_messages
):
    mocker.patch("vflexctl.device_interface.vflex.drain_incoming")
    mocker.patch("vflexctl.device_interface.vflex.protocol_decode_serial_number", return_value="fooSerial")
    mocker.patch("vflexctl.device_interface.vflex.get_millivolts_from_protocol_message", return_value=5000)
    mocker.patch("vflexctl.device_interface.vflex.protocol_decode_led_state", return_value=False)
    v_flex = VFlex(mock_io_port, safe_adjust=True)
    v_flex.wake_up()
    assert v_flex.current_voltage == 5000
    v_flex.current_voltage = 10000
    with pytest.raises(VoltageMismatchError) as exc:
        v_flex.set_voltage(12000)

    assert exc.value.stored_voltage == 10000
    assert exc.value.retrieved_voltage == 5000
