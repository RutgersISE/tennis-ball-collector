"""
Target tracking for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

import numpy as np

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x) - np.pi/2 # 90 degree correction for headings
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

class LatestSentTracker(object):

    def __init__(self):
        self.targets = np.empty((2, 0), dtype=np.float32)
        self.curr_x = self.curr_y = self.curr_phi = 0

    def get_target_rel(self):
        if not self.targets.size:
            return None
        self.agent = np.array([self.curr_x, self.curr_y])
        self.delta = self.targets - self.agent
        dist = np.sum(np.power(self.delta, 2), axis=1)
        target_idx = np.argmin(dist)
        target = self.delta[target_idx, ]
        rho, phi = cart2pol(*target)
        phi -= self.curr_phi
        return rho, phi, False

    def update_position(self, disp_rho, disp_phi):
        self.curr_phi += disp_phi
        self.curr_x += disp_rho*np.cos(self.curr_phi)
        self.curr_y += disp_rho*np.sin(self.curr_phi)

    def update_target_abs(self, targets):
        if targets:
            self.targets = np.array(targets)
        else:
            self.targets = np.empty((2, 0), dtype=np.float32)

    def update_agent_abs(self, x, y, phi):
        self.curr_x, self.curr_y, self.curr_phi = x, y, phi

    def update_target_rel(self, targets):
        rel_targets_x = np.array([x for x, _ in targets])
        rel_targets_y = np.array([y for _, y in targets])
        targets_rho, targets_phi = cart2pol(rel_targets_x, rel_targets_y)
        abs_targets_x = targets_rho*np.sin(-(targets_phi + self.curr_phi))
        abs_targets_x += self.curr_x
        abs_targets_y = targets_rho*np.cos(targets_phi + self.curr_phi)
        abs_targets_y += self.curr_y
        self.targets = np.vstack((abs_targets_x, abs_targets_y)).T
        
    def update_agent_rel(self, rho, phi):
        self.curr_phi += phi
        self.curr_x += rho*np.cos(self.curr_phi)
        self.curr_y += rho*np.sin(self.curr_phi)
