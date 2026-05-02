__all__ = ["MIDITriplet", "VFlexProtoMessage"]

type MIDITriplet = tuple[int, int, int]

type VFlexProtoMessage = list[int]
"""
A list of integers that, together, are one "message" or "command" to a connected VFlex.

For example, a voltage message is a list of integers:
- The command byte to set the voltage
- The high byte for the voltage value
- The low byte for the voltage value
"""
