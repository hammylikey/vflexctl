import pytest

from vflexctl.device_interface import VFlex
from vflexctl.device_interface import vflex as vflex_module
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


def test_get_voltage_updates_self_and_returns(mocker, mock_io_port):
    mocker.patch("vflexctl.device_interface.vflex.send_sequence")
    mock_drain = mocker.patch("vflexctl.device_interface.vflex.drain_incoming", return_value=["midi-bytes"])
    mock_protocol = mocker.patch(
        "vflexctl.device_interface.vflex.protocol_message_from_midi_messages",
        return_value=[4, 18, 0x2E, 0xE0],
    )
    mock_get_mv = mocker.patch(
        "vflexctl.device_interface.vflex.get_millivolts_from_protocol_message",
        return_value=12000,
    )

    v_flex = VFlex(mock_io_port, safe_adjust=False)
    assert v_flex.current_voltage is None

    result = VFlex.get_voltage.__wrapped__(v_flex, update_self=True)

    assert result == 12000
    assert v_flex.current_voltage == 12000

    mock_drain.assert_called_once_with(mock_io_port)
    mock_protocol.assert_called_once_with(["midi-bytes"])
    mock_get_mv.assert_called_once_with([4, 18, 0x2E, 0xE0])


def test_get_voltage_does_not_update_self_when_update_self_false(mocker, mock_io_port):
    mocker.patch("vflexctl.device_interface.vflex.send_sequence")
    mocker.patch("vflexctl.device_interface.vflex.drain_incoming", return_value=["midi-bytes"])
    mocker.patch(
        "vflexctl.device_interface.vflex.protocol_message_from_midi_messages",
        return_value=[4, 18, 0x2E, 0xE0],
    )
    mocker.patch(
        "vflexctl.device_interface.vflex.get_millivolts_from_protocol_message",
        return_value=12000,
    )

    v_flex = VFlex(mock_io_port, safe_adjust=False)
    v_flex.current_voltage = 5000

    result = VFlex.get_voltage.__wrapped__(v_flex, update_self=False)

    assert result == 12000
    assert v_flex.current_voltage == 5000


def test_get_led_state_updates_self_and_returns(mocker, mock_io_port):
    mocker.patch("vflexctl.device_interface.vflex.send_sequence")
    mocker.patch("vflexctl.device_interface.vflex.drain_incoming", return_value=["midi-bytes"])
    mocker.patch(
        "vflexctl.device_interface.vflex.protocol_message_from_midi_messages",
        return_value=[3, 15, 1],
    )
    mock_decode_led = mocker.patch("vflexctl.device_interface.vflex.protocol_decode_led_state", return_value=True)

    v_flex = VFlex(mock_io_port, safe_adjust=False)
    v_flex.led_state = False

    result = VFlex.get_led_state.__wrapped__(v_flex)

    assert result is True
    assert v_flex.led_state is True
    mock_decode_led.assert_called_once()


def test_set_voltage_sends_command_and_updates_voltage(mocker, mock_io_port):
    mock_set_voltage_command = mocker.patch(
        "vflexctl.device_interface.vflex.set_voltage_command",
        return_value=["encoded-voltage"],
    )
    mock_prepare_frame = mocker.patch(
        "vflexctl.device_interface.vflex.prepare_command_frame",
        return_value=["framed"],
    )
    mock_prepare_for_sending = mocker.patch(
        "vflexctl.device_interface.vflex.prepare_command_for_sending",
        return_value=["midi-seq"],
    )
    mock_send_sequence = mocker.patch("vflexctl.device_interface.vflex.send_sequence")
    mock_drain = mocker.patch("vflexctl.device_interface.vflex.drain_incoming", return_value=["midi-return"])
    mock_protocol = mocker.patch(
        "vflexctl.device_interface.vflex.protocol_message_from_midi_messages",
        return_value=[4, 18, 0x2E, 0xE0],
    )
    mock_get_mv = mocker.patch(
        "vflexctl.device_interface.vflex.get_millivolts_from_protocol_message",
        return_value=13000,
    )

    v_flex = VFlex(mock_io_port, safe_adjust=False)
    guard_mock = mocker.MagicMock(name="_guard_voltage")
    # Bypass the decorator behaviour for _guard_voltage in this test.
    v_flex._guard_voltage = guard_mock  # type: ignore[method-assign]

    VFlex.set_voltage.__wrapped__(v_flex, 13000)

    guard_mock.assert_called_once_with()
    mock_set_voltage_command.assert_called_once_with(13000)
    mock_prepare_frame.assert_called_once_with(["encoded-voltage"])
    mock_prepare_for_sending.assert_called_once_with(["framed"])
    mock_send_sequence.assert_called_once_with(mock_io_port, ["midi-seq"])
    mock_drain.assert_called_once_with(mock_io_port)
    mock_protocol.assert_called_once_with(["midi-return"])
    mock_get_mv.assert_called_once_with([4, 18, 0x2E, 0xE0])
    assert v_flex.current_voltage == 13000


def test_set_led_state_sends_commands_and_updates_state(mocker, mock_io_port):
    mock_set_led_cmd = mocker.patch(
        "vflexctl.device_interface.vflex.set_led_state_command",
        return_value=["encoded-led"],
    )
    mock_prepare_frame = mocker.patch(
        "vflexctl.device_interface.vflex.prepare_command_frame",
        return_value=["framed-led"],
    )
    mock_prepare_for_sending = mocker.patch(
        "vflexctl.device_interface.vflex.prepare_command_for_sending",
        return_value=["midi-led"],
    )
    mock_send_sequence = mocker.patch("vflexctl.device_interface.vflex.send_sequence")
    mock_drain = mocker.patch(
        "vflexctl.device_interface.vflex.drain_incoming",
        side_effect=(["ignored"], ["midi-return"]),
    )
    mock_protocol = mocker.patch(
        "vflexctl.device_interface.vflex.protocol_message_from_midi_messages",
        return_value=[3, 15, 1],
    )
    mock_decode_led = mocker.patch("vflexctl.device_interface.vflex.protocol_decode_led_state", return_value=True)

    v_flex = VFlex(mock_io_port, safe_adjust=False)

    VFlex.set_led_state.__wrapped__(v_flex, True)

    mock_set_led_cmd.assert_called_once_with(True)
    mock_prepare_frame.assert_called_once_with(["encoded-led"])
    mock_prepare_for_sending.assert_called_once_with(["framed-led"])

    # First send is the command, second send is the follow‑up GET_LED_STATE_SEQUENCE.
    assert mock_send_sequence.call_count == 2
    first_call, second_call = mock_send_sequence.call_args_list
    assert first_call.args == (mock_io_port, ["midi-led"])
    assert second_call.args == (mock_io_port, vflex_module.GET_LED_STATE_SEQUENCE)

    assert mock_drain.call_count == 2
    mock_protocol.assert_called_once_with(["midi-return"])
    mock_decode_led.assert_called_once()
    assert v_flex.led_state is True


def test_with_io_name_opens_ioport_and_respects_safe_adjust(mocker):
    mocker.patch("vflexctl.device_interface.vflex.mido.get_ioport_names", return_value=["VFlex Port"])
    mock_open = mocker.patch("vflexctl.device_interface.vflex.mido.open_ioport")
    mock_port = mocker.MagicMock(name="ioport")
    mock_open.return_value = mock_port

    v_flex = VFlex.with_io_name("VFlex Port", safe_adjust=False)

    mock_open.assert_called_once_with("VFlex Port")
    assert isinstance(v_flex, VFlex)
    assert v_flex.io_port is mock_port
    assert v_flex.safe_adjust is False


def test_with_io_name_raises_when_port_missing(mocker):
    mocker.patch("vflexctl.device_interface.vflex.mido.get_ioport_names", return_value=[])

    with pytest.raises(RuntimeError):
        VFlex.with_io_name("Missing Port")


def test_get_any_uses_default_port_name(mocker):
    mock_open = mocker.patch("vflexctl.device_interface.vflex.mido.open_ioport")
    mock_port = mocker.MagicMock(name="ioport")
    mock_open.return_value = mock_port

    v_flex = VFlex.get_any()

    mock_open.assert_called_once_with(vflex_module.DEFAULT_PORT_NAME)
    assert isinstance(v_flex, VFlex)
    assert v_flex.io_port is mock_port
