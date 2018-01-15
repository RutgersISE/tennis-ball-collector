"""
Control system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from math import atan, sqrt, pow
import numpy as np

class PointAndShootTrajector(object):

    def __init__(self, speed=60, turn_scaling=98, forward_scaling=115):
        self.speed = speed
        self.turn_scaling = turn_scaling
        self.forward_scaling = forward_scaling
        self.last_rho = None
        self.last_turn = None
        self.last_phi = None
        self.last_forward = None

    def _compute_turn(self, disp_phi, max_turn_time=.25, tol=1e-1):
        if disp_phi > tol:
            left_speed, right_speed = -self.speed, self.speed
        elif disp_phi < -tol:
            left_speed, right_speed = self.speed, -self.speed
        else:
            return None, None
        best_move_time = np.abs(disp_phi)/self.speed*self.turn_scaling
        if best_move_time > max_turn_time:
            true_move_time = best_move_time/2.0
        else:
            true_move_time = best_move_time
        disp_phi *= best_move_time/true_move_time
        stop = true_move_time >= best_move_time
        move = (left_speed, right_speed, true_move_time, stop)
        delta = (0, disp_phi)
        return move, delta

    def _compute_forward(self, disp_rho, max_forward_time=1.0):
        if np.isclose(disp_rho, 0, atol=1e-2):
             return None, None
        left_speed, right_speed = self.speed, self.speed
        best_move_time = np.abs(disp_rho)/self.speed*self.forward_scaling
        if best_move_time > max_forward_time:
            true_move_time = best_move_time/2.0
        else:
            true_move_time = best_move_time
        disp_rho *= best_move_time/true_move_time
        stop = true_move_time >= best_move_time
        move = (left_speed, right_speed, true_move_time, stop)
        delta = (disp_rho, 0)
        return move, delta

    def traject(self, rho, phi, max_turn_time=.25, max_forward_time=1.0):
        move, delta = self._compute_turn(phi, max_turn_time)
        if move:
            self.last_phi = phi
            return move, delta
        rho += 1.0
        move, delta = self._compute_forward(rho, max_forward_time)
        if move:
            self.last_rho = rho
            return move, delta
