"""
Control system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from math import atan, sqrt, pow
import numpy as np

class PointAndShootTrajector(object):

    def __init__(self, forward_speed=70, turn_speed=20, turn_scaling=98, forward_scaling=115,
                buffer_distance=1.5, max_turn_time=0.5, max_forward_time=1.0):
        self.forward_speed = forward_speed
        self.turn_speed = turn_speed
        self.turn_scaling = turn_scaling
        self.forward_scaling = forward_scaling
        self.buffer_distance = buffer_distance
        self.max_turn_time = max_turn_time
        self.max_forward_time = max_forward_time
        self.outer_radius = 2 + self.buffer_distance
        self.inner_radius = 1 + self.buffer_distance
        self.last_rho = None
        self.last_turn = None
        self.last_phi = None
        self.last_forward = None

    def _compute_turn(self, disp_phi, finish, tol=.5e-1):
        if disp_phi > tol:
            left_speed, right_speed = -self.turn_speed, self.turn_speed
        elif disp_phi < -tol:
            left_speed, right_speed = self.turn_speed, -self.turn_speed
        else:
            return None, None
        true_move_time = np.abs(disp_phi)/self.turn_speed*self.turn_scaling
        stop = True
        while not finish and true_move_time > self.max_turn_time:
            true_move_time /= 2.0
            disp_phi /= 2.0
            stop = False
        move = (left_speed, right_speed, true_move_time, stop)
        delta = (0, disp_phi)
        return move, delta

    def _compute_forward(self, disp_rho, finish, tol=1e-3):
        if np.abs(disp_rho) < tol:
             return None, None
        left_speed, right_speed = self.forward_speed, self.forward_speed
        if disp_rho > self.outer_radius:
            disp_rho -= self.outer_radius
        true_move_time = np.abs(disp_rho)/self.forward_speed*self.forward_scaling
        stop = True
        move = (left_speed, right_speed, true_move_time, stop)
        delta = (disp_rho, 0)
        return move, delta

    def traject(self, rho, phi, finish):
        move, delta = self._compute_turn(phi, finish)
        if move:
            return move, delta
        rho += self.buffer_distance
        move, delta = self._compute_forward(rho, finish)
        if move:
            return move, delta
        return None, None
