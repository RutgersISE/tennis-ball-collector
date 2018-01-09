import numpy as np

class NearestPointPlanner(object):

    def __init__(self):
        pass

    def plan(self, points):
        points = np.array(points)
        dist = np.sum(np.power(points, 2), axis=1)
        target_idx = np.argmin(dist)
        disp_x, disp_y = points[target_idx]
        return (disp_x, disp_y)
