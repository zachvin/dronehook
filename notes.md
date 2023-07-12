# File description
This file follows all my work in learning/understanding ArduPilot, specifically programming it with pymavlink.

# Translating from [MAVLink docs](https://mavlink.io/en/messages/common.html) to [pymavlink docs](https://mavlink.io/en/mavgen_python/)
MAVLink is a *protocol* which dictates the structure of messages sent over radio from the ground station computer or via USB from the onboard companion computer to the flight controller (FCU). pymavlink is a *code library* that allows you to use Python to write messages to the FCU according to the MAVLink protocol.
The MAVLink docs show a lot of different commands, but it is not immediately clear how to implement them in code. This is because we must look to pymavlink to understand how to structure our code. pymavlink code will include commands for us to write messages to the FCU via MAVLink, and it is at that point that we must look at the MAVLink docs to understand how to structure the messages. For now, let's take a look at how to write commands with pymavlink.
The general rule of thumb is that anything you find in the MAVLink docs is written in pymavlink in all lowercase with an extra word or two appended to it. See directly below for an example.

### MAVLink message
Some MAVLink messages are sent as *commands*. In the MAVLink docs, they are denoted by `MAV_CMD`. These commands are sent as type `COMMAND_INT` or `COMMAND_LONG` message. In pymavlink, this is done by writing the command in lowercase and appending `_send`, i.e. `the_connection.mav.command_int_send()`.

