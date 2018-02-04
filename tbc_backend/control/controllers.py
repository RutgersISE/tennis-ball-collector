#!/usr/bin/env python3
"""
Trajectory control system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

import numpy as np

class PointAndShootController(object):
    """Computes left and right speed given the desired heading
        Point and shoot first executes a turn and then drives forward.

        To make this method more robust, the following logic is followed:
            - If the target distance is outside an outer radius,
            turn until it is centered and move until at the outer radius.
            (DO NOT CAPTURE TARGET)
            - If the target distance is between an inner and outer radius,
            turn (slower) until it is centered and move to the target.
            (CAPTURE TARGET)
            - If the target distance is inside the inner radius, only move
            forward if centered (CAPTURE TARGET), otherwise back up and try
            again (DO NOT CAPTURE TARGET).

        Executing in this manner tends to allow more captures.
    """

    def __init__(self, turn_scaling=98, forward_scaling=115, min_speed=15,
                max_speed=60, buffer_distance=1.5, max_turn_time=0.5,
                max_forward_time=1.0):
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.turn_scaling = turn_scaling
        self.forward_scaling = forward_scaling
        self.buffer_distance = buffer_distance
        self.max_turn_time = max_turn_time
        self.max_forward_time = max_forward_time
        self.outer_radius = 2 + self.buffer_distance
        self.inner_radius = 1 + self.buffer_distance

    def _compute_turn(self, disp_phi, speed, finish=True):
        if disp_phi > 0:
            left_speed, right_speed = -speed, speed
        else:
            left_speed, right_speed = speed, -speed
        true_move_time = np.abs(disp_phi)/speed*self.turn_scaling
        stop = True
        while not finish and true_move_time > self.max_turn_time:
            true_move_time /= 2.0
            disp_phi /= 2.0
            stop = False
        move = (left_speed, right_speed, true_move_time, stop)
        delta = (0, disp_phi)
        return move, delta

    def _compute_forward(self, disp_rho, speed, finish=True):
        left_speed = right_speed =  speed
        true_move_time = np.abs(disp_rho)/np.abs(speed)*self.forward_scaling
        stop = True
        move = (left_speed, right_speed, true_move_time, stop)
        delta = (disp_rho, 0)
        return move, delta

    def control(self, rho, phi, finish, tol=2e-1):
        if phi > np.pi:
            phi = 2*np.pi - phi
        elif phi < -np.pi:
            phi = phi + 2*np.pi
        rho += self.buffer_distance
        outside = rho > self.outer_radius
        inside = rho < self.inner_radius
        between = not outside and not inside
        centered = abs(phi) < tol
        if outside:
            # when outside, make fast, coarse turns
            if not centered:
                move, delta = self._compute_turn(phi,
                                                 self.max_speed/2,
                                                 finish)
            else:
                rho -= self.outer_radius
                move, delta = self._compute_forward(rho,
                                                    self.max_speed,
                                                    finish)
        else:
            # when between circles, make slow, precise turns
            if not centered:
                move, delta = self._compute_turn(phi,
                                                 self.max_speed/4,
                                                 finish)
            else:
                move, delta = self._compute_forward(rho,
                                                    self.max_speed,
                                                    finish)
        return move, delta
