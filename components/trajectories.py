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

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

class PointAndShootTrajector(object):

    def __init__(self, speed=40, turn_scaling=98, forward_scaling=115):
        self.speed = speed
        self.turn_scaling = turn_scaling
        self.forward_scaling = forward_scaling

    def _compute_turn(self, disp_phi, max_turn_time=.25):
        if np.isclose(disp_phi, 0, atol=2.5e-1):
            return None, None
        elif disp_phi > 0:
            direction = np.array([-1, 1])
        else:
            direction = np.array([1, -1])
        left_speed, right_speed = self.speed*direction
        best_move_time = np.abs(disp_phi)/self.speed*self.turn_scaling
        true_move_time = min(best_move_time, max_turn_time)
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
        true_move_time = min(best_move_time, max_forward_time)
        disp_rho *= best_move_time/true_move_time
        stop = true_move_time >= best_move_time
        move = (left_speed, right_speed, true_move_time, stop)
        delta = (disp_rho, 0)
        return move, delta

    def traject(self, x, y, max_turn_time=.25, move_forward_time=1.0):
        rho, phi = cart2pol(x, y)
        rho *= 1.1
        move, delta = self._compute_turn(phi, max_turn_time)
        if move:
            yield move, delta
            _, _, _, stop = move
            if not stop:
                # if turning move is incomplete, allow vision to check position
                return
        move, delta = self._compute_forward(rho, max_forward_time)
        if move:
            yield move, delta
        return

if __name__ == "__main__":

    trajector = PointAndShootTrajector()
    print(trajector.traject(1, 1))
