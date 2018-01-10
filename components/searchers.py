import numpy as np

class RandomSearcher(object):

    def __init__(self, box_height, box_width):
        self.box_height, self.box_width = box_height, box_width
        self.curr_x = self.curr_y = self.curr_phi = 0
        self.next_x = np.random.uniform(0, self.box_width)
        self.next_y = np.random.uniform(0, self.box_height)

    def search(self):
        rel_x = self.next_x - self.curr_x
        rel_y = self.next_y - self.curr_y
        disp_rho = np.sqrt(rel_x**2 + rel_y**2)
        disp_phi = np.atan2(x, y) - self.curr_phi
        disp_x = rho*sin(phi)
        disp_y = rho*cos(phi)
        return disp_x, disp_y

    def update(self, disp_rho, disp_phi):
        self.curr_phi += disp_phi
        self.curr_x += disp_rho*np.cos(abs_phi)
        self.curr_y += disp_rho*np.sin(abs_phi)
        if np.isclose(self.curr_x, self.next_x, atol=5e-1) and \
            np.isclose(self.curr_y, self.next_y, atol=5e-1):
            self.next_x = np.random.uniform(0, self.box_width)
            self.next_y = np.random.uniform(0, self.box_height)
