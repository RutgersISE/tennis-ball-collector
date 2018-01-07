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

    def __init__(self, speed=50, turn_scaling=110, forward_scaling=115):
        self.speed = speed
        self.turn_scaling = turn_scaling
        self.forward_scaling = forward_scaling
        self.curr_left_speed = self.curr_right_speed = 0

    def _compute_turn(self, disp_x, disp_y):
        disp_phi = np.arctan2(disp_y, disp_x) - np.pi/2
        if np.isclose(disp_phi, 0, atol=1e-1):
            return 0, 0, 0
        elif disp_phi > 0:
            direction = np.array([-1, 1])
        else:
            direction = np.array([1, -1])
        left_speed, right_speed = self.speed*direction
        move_time = np.abs(disp_phi)/self.speed*self.turn_scaling
        return left_speed, right_speed, move_time

    def _compute_forward(self, disp_x, disp_y):
        disp_rho = np.sqrt(disp_x**2 + disp_y**2)
        if np.isclose(disp_rho, 0, atol=1e-1):
             return 0, 0, 0
        direction = np.array([1, 1])
        left_speed, right_speed = self.speed*direction
        move_time = np.abs(disp_rho)/self.speed*self.forward_scaling
        return left_speed, right_speed, move_time

    def plan(self, disp_x, disp_y):
        left_speed, right_speed, move_time = self._compute_turn(disp_x, disp_y)
        yield left_speed, right_speed, move_time
        left_speed, right_speed, move_time = self._compute_forward(disp_x, disp_y)
        yield left_speed, right_speed, move_time

def move(port, baud):
    controller = ArduinoController(port, baud)
    planner = PointAndShootPlanner()
    while True:
        object_points = yield # they're called coroutines and I just learned about them too
        left_speed, right_speed = planner.plan(object_points)
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
    planner = PointAndShootPlanner()
    while True:
        try:
            raw_instructions = input("robot: ")
            if "exit" in raw_instructions:
                break
            command_level, arg_1, arg_2 = raw_instructions.split()
            if "speed" in command_level:
                left_speed, right_speed = arg_1, arg_2
                commander.command(left_speed, right_speed)
            elif "point" in command_level:
                disp_x, disp_y = float(arg_1), float(arg_2)
                for left_speed, right_speed, move_time in planner.plan(disp_x, disp_y):
                    if move_time == 0:
                        continue
                    commander.command(left_speed, right_speed)
                    time.sleep(move_time)
                commander.command(0, 0)
        except KeyboardInterrupt:
            break
    commander.command(0, 0)
