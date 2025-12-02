from vflexctl.midi_transport import senders
from vflexctl.types import MIDITriplet


def test_send_triplet_sends_single_midi_message(mocker):
    """send_triplet should build a MIDI message and send it once via the output port."""
    output = mocker.MagicMock()

    # Patch sleep so the test is fast and we can assert it was called.
    mock_sleep = mocker.patch("vflexctl.midi_transport.senders.sleep")

    triplet: MIDITriplet = (0x90, 0x00, 0x01)

    senders.send_triplet(output, triplet, pause=0.5)

    # One message should have been sent.
    output.send.assert_called_once()
    sent_message = output.send.call_args.args[0]
    assert sent_message.bytes() == list(triplet)

    # sleep should have been called with the pause value we passed in.
    mock_sleep.assert_called_once_with(0.5)


def test_send_sequence_calls_send_triplet_for_each_triplet(mocker):
    """send_sequence should delegate to send_triplet once per triplet, preserving order."""
    output = mocker.MagicMock()
    sequence: list[MIDITriplet] = [
        (0x90, 0x00, 0x01),
        (0x90, 0x00, 0x02),
        (0x90, 0x01, 0x03),
    ]

    mock_send_triplet = mocker.patch("vflexctl.midi_transport.senders.send_triplet")

    senders.send_sequence(output, sequence)

    # We expect one call per triplet, in order.
    assert mock_send_triplet.call_count == len(sequence)
    assert [call.args[1] for call in mock_send_triplet.call_args_list] == sequence
    # First arg should always be the same output.
    assert all(call.args[0] is output for call in mock_send_triplet.call_args_list)


def test_send_sequence_logs_sequence(mocker):
    """send_sequence should log the sequence it is about to send."""
    mock_log = mocker.patch.object(senders, "log")
    output = mocker.MagicMock()
    sequence: list[MIDITriplet] = [(0x90, 0x00, 0x01)]

    # Patch send_triplet so we don't rely on its behaviour here.
    mocker.patch("vflexctl.midi_transport.senders.send_triplet")

    senders.send_sequence(output, sequence)

    mock_log.info.assert_called_once_with("Sending MIDI Sequence", sequence=sequence)
