"""
Target tracking for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from threading import Lock
import numpy as np

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x) - np.pi/2
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

class ThreadsafeTracker(object):

    def __init__(self, in_view=True, buffer_distance=0):
        self.targets = np.empty((2, 0), dtype=np.float32)
        self.buffer_distance = buffer_distance
        self.in_view = in_view
        self.curr_x = self.curr_y = self.curr_phi = 0
        self.target_lock = Lock()
        self.agent_lock = Lock()

    @property
    def targets_abs(self):
        with self.target_lock:
            return self.targets

    @targets_abs.setter
    def targets_abs(self, targets):
        with self.target_lock:
            if targets is None:
                self.targets = np.empty((2, 0), dtype=np.float32)
            else:
                self.targets = np.array(targets)

    @property 
    def targets_rel(self):
        targets = self.targets_abs
        curr_x, curr_y, curr_phi = self.agent_abs
        if not targets.size or curr_x is None:
            return None
        agent = np.array([curr_x, curr_y])
        delta = targets - agent
        if self.in_view:
            exclude = np.logical_and(np.abs(delta[:, 0]) < 1,
                                     np.abs(delta[:, 1]) < 1)
            delta = delta[~exclude]
        if not delta.size:
            return None
        dist = np.sqrt(np.sum(np.power(delta, 2), axis=1))
        angle = -(curr_phi - np.arctan2(delta[:, 1], delta[:, 0]))
        target_idx = np.argmin(dist)
        rho = dist[target_idx]
        phi = angle[target_idx]
        if phi > np.pi:
            phi = 2*np.pi - phi
        return rho, phi, self.in_view

    @targets_rel.setter
    def targets_rel(self, targets):
        curr_x, curr_y, curr_phi = self.agent_abs
        if curr_x is None:
            return
        rel_targets_x = np.array([x for x, _ in targets])
        rel_targets_y = np.array([y for _, y in targets])
        targets_rho, targets_phi = cart2pol(rel_targets_x, rel_targets_y)
        abs_targets_x = targets_rho*np.cos((targets_phi + curr_phi))
        abs_targets_x += curr_x
        abs_targets_y = targets_rho*np.sin(targets_phi + curr_phi)
        abs_targets_y += curr_y
        targets = np.vstack((abs_targets_x, abs_targets_y)).T
        self.targets_abs = targets

    @property
    def agent_abs(self):
        with self.agent_lock:
            return self.curr_x, self.curr_y, self.curr_phi

    @agent_abs.setter
    def agent_abs(self, position):
        with self.agent_lock:
            self.curr_x, self.curr_y, self.curr_phi = position

    @property
    def agent_rel(self):
        return 0, 0, 0

    @agent_rel.setter
    def agent_rel(self, position):
        rho, phi = position
        with self.agent_lock:
            self.curr_phi += phi
            self.curr_x += rho*np.cos(self.curr_phi)
            self.curr_y += rho*np.sin(self.curr_phi)

