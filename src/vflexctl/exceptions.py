__all__ = [
    "InvalidProtocolMessageLengthError",
    "InvalidProtocolMessageError",
    "IncorrectCommandByte",
    "UnsafeAdjustmentError",
    "SerialNumberMismatchError",
    "VoltageMismatchError",
    "UnsupportedFirmwareVersionError",
]


class InvalidProtocolMessageError(ValueError):

    def __init__(self, protocol_message: list[int], message: str = "Invalid protocol message"):
        self.protocol_message = protocol_message
        super().__init__(message)


class InvalidProtocolMessageLengthError(InvalidProtocolMessageError):
    """
    On receiving a message, the length is not correct for the type of message that should
    come back from the VFlex. For example, we receive a serial number response that isn't
    of length 10.
    """

    def __init__(
        self,
        protocol_message: list[int],
        expected_length: int,
    ):
        message = f"Expected {expected_length} bytes but got {len(protocol_message)}"
        super().__init__(protocol_message, message)


class IncorrectCommandByte(InvalidProtocolMessageError):
    """
    On receiving a message, the command byte was not correct for the type of message
    we're trying to decode. For example, a voltage command is being passed to
    ``protocol_decode_firmware_version``, where trying to decode it would give garbage data.
    """

    def __init__(
        self,
        protocol_message: list[int],
        expected_command: int,
    ):
        message = f"Expected command number {expected_command}, but got {protocol_message[1]}"
        super().__init__(protocol_message, message)


class UnsafeAdjustmentError(Exception):
    """
    Base class for exceptions related to making adjustments on a VFlex where the target
    might not be correct, or the adjustment is otherwise "unsafe" to do.

    "Unsafe" for this exception generally means "setting on the wrong VFlex" or trying
    to adjust a feature that the VFlex doesn't have.
    """

    def __init__(self, ex_message: str | None = None):
        msg = "An unsafe adjustment to the connected VFlex was stopped."
        if ex_message is not None:
            msg += "\n" + ex_message
        super().__init__(msg)


class SerialNumberMismatchError(UnsafeAdjustmentError):
    """
    Raised when an adjustment is being made to a VFlex, but the serial number has changed
    between adjustments.
    """

    def __init__(self, old_serial_number: str | None = None, new_serial_number: str | None = None):
        msg = ["The serial number does not match the last fetched serial number."]
        if old_serial_number is not None:
            msg.append(f"First fetched serial number: {old_serial_number}")
        if new_serial_number is not None:
            msg.append(f"Last fetched serial number: {new_serial_number}")

        super().__init__("\n\t".join(msg).strip())


class VoltageMismatchError(UnsafeAdjustmentError):
    """
    Raised when an adjustment is being made to a VFlex, but when checking the voltage to help identify
    that the same VFlex is being targeted, the voltage changes.

    :param stored_voltage: The voltage that was stored (or previously read) - optional
    :param retrieved_voltage: The currently retrieved voltage - optional
    """

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


class UnsupportedFirmwareVersionError(UnsafeAdjustmentError):
    """
    Raised when an adjustment is being made to a VFlex, but for a feature that the firmware
    version of the VFlex does not have or support.

    :param firmware_version: The firmware version retrieved from the connected VFlex - optional
    :param required_version: The firmware version that needs to be supported in order to support the feature - optional
    """

    def __init__(self, firmware_version: str | None = None, required_version: str | None = None):
        msg = ["Unsupported firmware version for this adjustment."]
        if firmware_version is not None:
            msg.append(f"Firmware version: {firmware_version.upper().removeprefix("APP.")}")
        if required_version is not None:
            msg.append(f"Minimum required version: {required_version}")
        super().__init__(" ".join(msg).strip())
