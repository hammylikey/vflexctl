__all__ = [
    "InvalidProtocolMessageLengthError",
    "InvalidProtocolMessageError",
    "IncorrectCommandByte",
    "UnsafeAdjustmentError",
    "SerialNumberMismatchError",
    "VoltageMismatchError",
]


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


class UnsafeAdjustmentError(Exception):

    def __init__(self, ex_message: str | None = None):
        msg = "An unsafe adjustment to the connected VFlex was stopped."
        if ex_message is not None:
            msg += "\n" + ex_message
        super().__init__(msg)


class SerialNumberMismatchError(UnsafeAdjustmentError):

    def __init__(self, old_serial_number: str | None = None, new_serial_number: str | None = None):
        msg = ["The serial number does not match the last fetched serial number."]
        if old_serial_number is not None:
            msg.append(f"First fetched serial number: {old_serial_number}")
        if new_serial_number is not None:
            msg.append(f"Last fetched serial number: {new_serial_number}")

        super().__init__("\n\t".join(msg).strip())


class VoltageMismatchError(UnsafeAdjustmentError):
    stored_voltage: int | None = None
    retrieved_voltage: int | None = None

    def __init__(self, stored_voltage: int | None = None, retrieved_voltage: int | None = None):
        msg = ["On a voltage check, the current stored voltage did not match the voltage gathered from the device."]
        if stored_voltage is not None:
            self.stored_voltage = stored_voltage
            msg.append(f"Stored voltage: {stored_voltage}")
        if retrieved_voltage is not None:
            self.retrieved_voltage = retrieved_voltage
            msg.append(f"Last fetched voltage: {retrieved_voltage}")

        super().__init__("\n\t".join(msg).strip())
