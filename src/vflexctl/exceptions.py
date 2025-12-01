class InvalidProtocolMessageError(ValueError):

    def __init__(self, protocol_message: list[int], message: str = "Invalid protocol message"):
        self.protocol_message = protocol_message
        super().__init__(message)


class InvalidProtocolMessageLengthError(InvalidProtocolMessageError):

    def __init__(
        self,
        protocol_message: list[int],
        expected_length: int,
    ):
        message = f"Expected {expected_length} bytes but got {len(protocol_message)}"
        super().__init__(protocol_message, message)


class IncorrectCommandByte(InvalidProtocolMessageError):
    def __init__(
        self,
        protocol_message: list[int],
        expected_command: int,
    ):
        message = f"Expected command number {expected_command}, but got {protocol_message[1]}"
        super().__init__(protocol_message, message)


class SerialNumberMismatchError(ValueError):

    def __init__(self, old_serial_number: str | None = None, new_serial_number: str | None = None):
        msg = ["The serial number does not match the last fetched serial number."]
        if old_serial_number is not None:
            msg.append(f"First fetched serial number: {old_serial_number}")
        if new_serial_number is not None:
            msg.append(f"Last fetched serial number: {new_serial_number}")

        super().__init__("\n\t".join(msg).strip())
