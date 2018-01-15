"""
Control system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from math import atan, sqrt, pow
import numpy as np

class PointAndShootTrajector(object):

    def __init__(self, speed=60, turn_scaling=98, forward_scaling=115,
                buffer_distance=1.5, max_turn_time=0.5, max_forward_time=1.0):
        self.speed = speed
        self.turn_scaling = turn_scaling
        self.forward_scaling = forward_scaling
        self.buffer_distance = buffer_distance
        self.max_turn_time = max_turn_time
        self.max_forward_time = max_forward_time
        self.last_rho = None
        self.last_turn = None
        self.last_phi = None
        self.last_forward = None

    def _compute_turn(self, disp_phi, tol=1e-1):
        if disp_phi > tol:
            left_speed, right_speed = -self.speed/4.0, self.speed/4.0
        elif disp_phi < -tol:
            left_speed, right_speed = self.speed/4.0, -self.speed/4.0
        else:
            return None, None
        true_move_time = np.abs(disp_phi)/self.speed*4.0*self.turn_scaling
        stop = True
        while true_move_time > self.max_turn_time:
            true_move_time /= 2.0
            disp_phi /= 2.0
            stop = False
        move = (left_speed, right_speed, true_move_time, stop)
        delta = (0, disp_phi)
        return move, delta

    def _compute_forward(self, disp_rho, tol=1e-3):
        if np.abs(disp_rho) < tol:
             return None, None
        left_speed, right_speed = self.speed, self.speed
        true_move_time = np.abs(disp_rho)/self.speed*self.forward_scaling
        stop = True
        while true_move_time > self.max_forward_time:
            true_move_time /= 2.0
            disp_rho /= 2.0
            stop = False
        move = (left_speed, right_speed, true_move_time, stop)
        delta = (disp_rho, 0)
        return move, delta

    def traject(self, rho, phi):
        move, delta = self._compute_turn(phi)
        if move:
            return move, delta
        rho += self.buffer_distance
        move, delta = self._compute_forward(rho)
        if move:
            return move, delta
        return None, None
