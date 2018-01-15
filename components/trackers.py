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

    def update(self, targets):
        self.targets = deepcopy(targets)

    def get_target(self):
        if not self.targets:
            return None
        rho, phi = cart2pol(*self.targets[0])
        return rho, phi
