import mido

from vflexctl.midi_transport.receivers import drain_once, drain_incoming


def test_drain_once_drains_as_tuple_when_list_is_returned(mocker):
    message_bytes = [144, 0, 1]
    messages = [mido.Message.from_bytes(message_bytes) for _ in range(5)]

    def iter_pending_messages():
        for message in messages:
            yield message
        return

    mock_port = mocker.MagicMock(
        iter_pending=iter_pending_messages,
    )
    result = drain_once(mock_port)
    for msg in result:
        assert isinstance(msg, tuple)
        assert msg == (144, 0, 1)


def test_drain_incoming_returns_empty_list_if_seconds_is_negative():
    response = drain_incoming(None, seconds=-1)
    assert response == []


def test_drain_incoming_keeps_draining_while_in_the_loop(mocker):
    message = mido.Message.from_bytes([144, 0, 1])

    iterator_call_count: int = 0

    def iter_pending_messages():
        nonlocal iterator_call_count
        if iterator_call_count == 0:
            yield message
        iterator_call_count += 1
        return

    mock_port = mocker.MagicMock(iter_pending=iter_pending_messages)
    result = drain_incoming(mock_port)
    assert result == [(144, 0, 1)]
    # There should be way more than 5 calls, but this seems like a sensible minimum
    # to be able to say "yes, it tries to get all waiting messages"
    assert iterator_call_count > 5
