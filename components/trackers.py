import numpy as np
from copy import deepcopy

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
        self.targets = None
        self.curr_x = self.curr_y = self.curr_phi = 0

    def update_target(self, targets):
        self.targets = deepcopy(targets)

    def get_target(self):
        if not self.targets:
            return None
        rho, phi = cart2pol(*self.targets[0])
        return rho, phi, False

    def update_position(self, disp_rho, disp_phi):
        self.curr_phi += disp_phi
        self.curr_x += disp_rho*np.cos(self.curr_phi)
        self.curr_y += disp_rho*np.sin(self.curr_phi)
