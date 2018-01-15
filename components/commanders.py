#!/usr/bin/env python3
"""
Control system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from serial import Serial
import time

class ArduinoCommander(object):

    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.serial = Serial(self.port, self.baud, timeout=None)
        time.sleep(2)
        self.last_message = None

    def _send(self, left_speed, right_speed):
        left_speed, right_speed = int(left_speed), int(right_speed)
        message = "%d %d\r\n" % (left_speed, right_speed)
        if message == self.last_message:
            # sending this message is redundant
            return
        self.serial.flush()
        self.serial.write(message.encode())
        self.last_message = message
        time.sleep(.05)

    def command(self, left_speed, right_speed, move_time=None, stop=False):
        self._send(left_speed, right_speed)
        if move_time is not None:
            time.sleep(move_time)
        if stop:
            self._send(0, 0)

class DummyCommander(object):

    def __init__(self):
        pass

    def command(self, left_speed, right_speed, move_time=None):
        print("command:", left_speed, right_speed, move_time)
