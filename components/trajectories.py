#!/usr/bin/env python3
"""
Control system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from math import atan, sqrt, pow
import numpy as np

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x) - np.pi/2 # 90 degree correction for headings
    return(rho, phi)

class PointAndShootTrajector(object):

    def __init__(self, speed=60, turn_scaling=110, forward_scaling=113):
        self.speed = speed
        self.turn_scaling = turn_scaling
        self.forward_scaling = forward_scaling
        self.curr_left_speed = self.curr_right_speed = 0

    def _select_target(self, object_points):
        dist = np.sum(np.power(object_points, 2), axis=1)
        target_idx = np.argmin(dist)
        disp_x, disp_y = object_points[target_idx]
        return disp_x, disp_y

    def _compute_turn(self, disp_x, disp_y):
        disp_phi = np.arctan2(disp_y, disp_x) - np.pi/2
        if np.isclose(disp_phi, 0, atol=1.5e-1):
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

    def traject(self, disp_x, disp_y, max_move_time=.25):
        left_speed, right_speed, move_time = self._compute_turn(disp_x, disp_y)
        if move_time != 0:
            move_time = min(move_time, max_move_time)
            return left_speed, right_speed, move_time
        left_speed, right_speed, move_time = self._compute_forward(disp_x, disp_y)
        if move_time != 0:
            move_time = min(move_time, max_move_time)
            return left_speed, right_speed, move_time
        return 0, 0, 0
