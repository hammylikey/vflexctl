# vflexctl

An unofficial CLI for setting the voltage on VFLEX devices with MIDI control.

Why? I dunno, I like the idea of being able to work this without needing a website?

## Installation

This requires that you have `pipx` installed on your system, using Python 3.12 or later.

Using `pipx`, install this tool with:

pipx install vflexctl

## Usage

### Reading your VFlex

To read your VFlex's current state, use the `read` command:

$ vflexctl read
VFlex Serial Number: <your serial here>
Current Voltage: 12.00
LED State: Always On

You can set either your voltage, LED state (always on or not always on), or both:

vflexctl set -v <voltage> -l <always-on|disabled>

### Voltage

Voltage is set with the `--voltage` or `-v` flag, with your volts as XX.XX. For example:

vflexctl set -v 12
vflexctl set -v 5.50
vflexctl set -v 48.5
vflexctl set -v 12.0000001

The VFlex communication over MIDI limits the maximum voltage to around 65.5V
(the limit of a 16-bit integer). Trying to set a higher value will prevent the voltage
from being set.

### LED state

LED state is set using the `--led` or `-l` flag, with the value as either:

vflexctl set -l always-on
vflexctl set -l disabled

To set both voltage and LED state, use both flags (in any order).

### --deep-adjust

--deep-adjust is a flag to use the old (<= 0.1.2) setting behaviour.

Since 0.2.0, the tool only sends a serial number request after the initial wake-up.
This should work to set the voltage more quickly, but you can add this flag to be
extra sure:

vflexctl --deep-adjust set -v 12
vflexctl set -v 12

Open a PR (or an issue) if this doesn’t work.

## The VFlex object

If you're using this as a module (firstly, yay! welcome!) you have access to the VFlex object.

```python
from vflexctl.device_interface import VFlex
```

Hopefully the docstrings make sense, but to summarise:


#### Methods

- `get_any(cls, ...)` - This gets the first VFlex that matches the default MIDI port name ("Werewolf vFlex")
  - This is used by the CLI to get the connected VFlex
- `with_io_name(cls, name: str, ...)` - This initialises a VFlex with a MIDO BaseIOPort using the provided name.
    This is useful if you want to connect to a specific one and know what the port name is using `mido`. 
- `initial_wake_up()` - run this to grab the serial number, and current LED state and Voltage

#### Properties

- `io_port` - if you want to send MIDI directly, you can use this as a way to send messages


## Current state

This seems to be working. Setting values takes a bit longer than the web UI, since the
tool performs a “startup dance” each time something is set (read serial, read LED,
read voltage).

~~An improvement could be to test if the setting works if it only reads the serial, and
re-waking the device might not be needed since most operations are less than 5 seconds.~~
Implemented since 0.2.0

The assumption is that this works as long as you only have one device connected.
Unless it becomes important, device selection adds more complexity than is currently
needed.

## Developer info

This project uses poetry for managing dependenies and building, built with Python 3.12.10. Unless there's
a huge shift and poetry becomes terrible, please don't commit in a requirements.txt.

There are `black` rules for formatting in pyproject.toml as well - if your IDE formats on save, it (should)
pick these up and format your files for you. The project also uses `mypy` for typing. Since this has a `py.typed`,
you likely want to run `mypy .` and fix any typing issues before opening a PR or something.

Fork/pull/PR as you want!

---

This is an independent hobby project.
It is not affiliated with, endorsed by, or connected to any company.
All product names, trademarks, and brands are the property of their respective owners.