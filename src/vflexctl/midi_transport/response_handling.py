from vflexctl.device_interface.common_commands import GET_VOLTAGE_COMMAND

def guard_response(response: list[int], expected_command: list[int]):
    if response[1:][:len(expected_command)] != expected_command:
        raise ValueError()

def millivolts_from_get_voltage_response(response: list[int]) -> int:
    """
    From a response for the command to get the current voltage, parse/gather
    the millivolts.
    :param response:
    :return:
    """
    if response[0] != 4:
        raise ValueError("Get Voltage response should return a response of length 4")
    guard_response(response, GET_VOLTAGE_COMMAND)
    high_byte, low_byte = response[2], response[3]
    return (high_byte << 8) | low_byte
