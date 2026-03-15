from vflexctl.protocol import VFlexProto
from vflexctl.types import VFlexProtoMessage


def get_firmware_version_command() -> VFlexProtoMessage:
    """
    Create the protocol message to get the firmware version from the device.

    Expect that the firmware version string comes back as "APP.##.##.##" (# is a number).

    :return: Protocol message to send to the device.
    """
    return [VFlexProto.CMD_GET_FIRMWARE_VERSION]


def get_hardware_revision_command() -> VFlexProtoMessage:
    """
    Create the protocol message to get the hardware revision from the device.

    :return: Protocol message to send to the device.
    """
    return [VFlexProto.CMD_GET_HARDWARE_REVISION]
