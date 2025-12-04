########################
vflexctl
########################

An unofficial cli for setting the voltage on VFLEX devices with MIDI control

Why? I dunno, I like the idea of being able to work this without needing a website?

************
Installation
************

This requires that you have ``pipx`` installed on your system, using Python 3.12 or later.

Using ``pipx``, install this tool with::

    pipx install vflexctl

************
Usage
************

===================
Reading your VFlex
===================

To read your VFlex's current state, use the ``read`` command::

    $ vflexctl read
    VFlex Serial Number: <your serial here>
    Current Voltage: 12.00
    LED State: Always On

You can set either your voltage, LED state (always on or not always on), or both::

    vflexctl set -v <voltage> -l <always-on|disabled>

Voltage is set with the ``--voltage`` or ``-v`` flag, with your volts as XX.XX. For example::

    vflexctl set -v 12 # Sets to 12V
    vflexctl set -v 5.50 # Sets to 5V
    vflexctl set -v 48.5 # Sets to 48.5V (if this exists?)
    vflexctl set -v 12.0000001 # Rounds to 12.00, and sets 12V

The VFlex communication over MIDI limits the max that you can set this to be around
65.5V (the limit of a 16-bit integer) Trying to set higher than this will prevent setting voltage.

LED state is set using the ``--led`` or ``-l`` flag, with the value as either::

    vflexctl set -l always-on # The default "LED always on" behaviour
    vflexctl set -l disabled # The non-default "LED is off after a few minutes, except for error"

To set both, use both flags (as defined above) in any order.


==============
Current state
==============

This seems to be working. Setting values takes a bit longer than the web, since I've set this up to do the "startup dance"
every time we try to set something (read serial, then read LED, then read Voltage).

An improvement could be to test if the setting works if it only reads the serial, and re-waking the
device might not be needed since most operations are less than 5 seconds.

The plan is that this will work as long as you only have *one* inserted. Unless it's extremely important, building selection is more work than what's needed.

---
---

This is an independent hobby project.  
It is not affiliated with, endorsed by, or connected to any company.  
All product names, trademarks, and brands are the property of their respective owners.
