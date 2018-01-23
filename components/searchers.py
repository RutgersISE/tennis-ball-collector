import numpy as np

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x) - np.pi/2 # 90 degree correction for headings
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

class RandomSearcher(object):

    def __init__(self, x=0, y=0):
        self._n = 0

    def get_target(self):
        rel_x = self.next_x - self.curr_x
        rel_y = self.next_y - self.curr_y
        disp_rho = np.sqrt(rel_x**2 + rel_y**2)
        disp_phi = np.arctan2(rel_x, rel_y) - self.curr_phi
        disp_x = disp_rho*np.sin(disp_phi)
        disp_y = disp_rho*np.cos(disp_phi)
        rho, phi = cart2pol(disp_x, disp_y)
        self._n += 1
        if self._n % 2:
            return rho, 0, True
        else:
            return 0, phi, True

    def update_position(self, disp_rho, disp_phi):
        self.curr_phi += disp_phi
        self.curr_x += disp_rho*np.cos(self.curr_phi)
        self.curr_y += disp_rho*np.sin(self.curr_phi)
        if np.isclose(self.curr_x, self.next_x, atol=5e-1) and \
            np.isclose(self.curr_y, self.next_y, atol=5e-1):
            self.next_x = np.random.uniform(0, self.box_width)
            self.next_y = np.random.uniform(0, self.box_height)
