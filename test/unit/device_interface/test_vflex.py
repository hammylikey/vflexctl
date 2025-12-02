import pytest

from vflexctl.device_interface import VFlex


@pytest.fixture
def mock_io_port(mocker):
    yield mocker.MagicMock(name="mock_io_port")


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
