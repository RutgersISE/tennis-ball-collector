#!/usr/bin/env python3
"""
Control system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from serial import Serial
import sys
import time
from math import atan, sqrt, pow
import numpy as np

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x) - np.pi/2 # 90 degree correction for headings
    return(rho, phi)

class ArduinoCommander(object):

    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.serial = Serial(self.port, self.baud, timeout=None)
        time.sleep(2)

    def command(self, left_speed, right_speed):
        left_speed, right_speed = int(left_speed), int(right_speed)
        message = "%d %d\r\n" % (left_speed, right_speed)
        self.serial.flush()
        self.serial.write(message.encode())

class PointAndShootPlanner(object):

    def __init__(self, min_speed=20, max_speed=150):
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.curr_left_speed = self.curr_right_speed = 0

    def _compute_trajectory(self, disp_x, disp_y):
        #disp_rho = np.sqrt(disp_x**2 + disp_y**2)
        disp_phi = np.arctan2(disp_y, disp_x) - np.pi/2 # 90 degree correction for headings
        print(disp_phi)
        if not np.isclose(disp_phi, 0, rtol=2e-1, atol=2e-1):
            # if angle is significantly different, then turn
            if disp_phi > 0:
                return -1, 0
            else:
                return 0, -1
        else:
            return 1, 1

    def plan(self, disp_x, disp_y):
        left_dir, right_dir = self._compute_trajectory(disp_x, disp_y)
        left_speed = self.speed*left_dir
        right_speed = self.speed*right_dir
        return left_speed, right_speed, move_time

def move(port, baud):
    controller = ArduinoController(port, baud)
    planner = PointAndShootPlanner()
    while True:
        object_points = yield # they're called coroutines and I just learned about them too
        print(object_points)
        left_speed, right_speed = planner.plan(object_points)
        print(left_speed, right_speed)
        controller.control(left_speed, right_speed)

if __name__ == "__main__":
    from argparse import ArgumentParser
    import sys

    parser = ArgumentParser(description="Listen for commands to execute on robot.")
    parser.add_argument("--port",  dest="port", type=str, default="/dev/ttyACM0",
                        help="port address of motor controller.")
    parser.add_argument("--baud", dest="baud", type=int, default=9600,
                        help="baud rate of motor controller.")
    args = parser.parse_args()

    commander = ArduinoCommander(args.port, args.baud)
    planner = PointAndShootPlanner(args.speed)
    while True:
        try:
            raw_instructions = input("robot: ")
            if "exit" in raw_instructions:
                break
            command_level, arg_1, arg_2 = raw_instructions.split()
            if "speed" in command_level:
                left_speed, right_speed = arg_1, arg_2
                commander.command(left_speed, right_speed)
            #elif "point" in command_level:
            #    disp_x, disp_y = arg_1, arg_2
            #    left_speed, right_speed, move_time = planner.plan(disp_x, disp_y)
        except BaseException as e:
            print(e)
            break
    commander.command(0, 0)
