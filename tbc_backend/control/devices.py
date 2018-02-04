#!/usr/bin/env python3
"""
Motor controller commanders for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

import time

from threading import Timer
from serial import Serial

class ArduinoRobot(object):

    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.serial = Serial(self.port, self.baud, timeout=None)
        time.sleep(2)
        self.curr_message = None
        self._timer = None

    def _send(self, left_speed, right_speed):
        left_speed, right_speed = int(left_speed), int(right_speed)
        next_message = "%d %d\r\n" % (left_speed, right_speed)
        if next_message == self.curr_message:
            # sending this message is redundant
            return
        self.serial.flush()
        self.serial.write(next_message.encode())
        self.curr_message = next_message
        time.sleep(.10) # allows arduino to timeout

    def _wait(self, move_time):
        if move_time is None:
            return
        if self._timer:
            self._timer.cancel()
        self._timer = Timer(move_time, self.stop)
        self._timer.start()

    def command(self, left_speed, right_speed, move_time=None, stop=False):
        self._send(left_speed, right_speed)
        self._wait(move_time)

    def stop(self):
        self._send(0, 0)

    def __del__(self):
        self.stop()

class DummyCommander(object):

    def __init__(self):
        pass

    def command(self, left_speed, right_speed, move_time=None, stop=False):
        print("command:", left_speed, right_speed, move_time, stop)
        time.sleep(move_time)
