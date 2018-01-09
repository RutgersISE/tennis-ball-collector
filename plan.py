import threading
import time
from math import cos, sin, atan2, sqrt
import numpy as np

from components.communication import Publisher, Subscriber
from components.planners import NearestPointPlanner

position_lock = threading.Lock()
abs_x, abs_y, abs_phi = 0, 0, 0

def listen_position_rel():
    global abs_x, abs_y, abs_phi
    position_subscriber = Subscriber("position_rel", "5558")
    while True:
        disp_rho, disp_phi = position_subscriber.listen()
        position_lock.acquire()
        old_x, old_y = abs_x, abs_y
        abs_phi += disp_phi
        abs_x += disp_rho*cos(abs_phi)
        abs_y += disp_rho*sin(abs_phi)
        position_lock.release()

candidates_lock = threading.Lock()
candidates = np.empty((0, 2), dtype=np.float32)

def listen_in_view():
    global abs_x, abs_y, abs_phi, candidates
    in_view_subscriber = Subscriber("in_view", "5556")
    while True:
        rel_points = in_view_subscriber.listen()
        polar_points = [(sqrt(x**2 + y**2), atan2(x, y)) for x, y in rel_points]
        curr_x, curr_y, curr_phi = abs_x, abs_y, abs_phi
        abs_points = [(curr_x + rho*sin(curr_phi + phi), curr_y + rho*cos(curr_phi + phi)) for rho, phi in polar_points]
        abs_points = [(round(x, 1), round(y, 1)) for x, y in abs_points]
        candidates_lock.acquire()
        candidates = np.vstack((candidates, np.array(abs_points)))
        candidates = np.unique(candidates, axis=0)
        candidates_lock.release()

def main():
    global candidates
    target_publisher = Publisher("target_rel", "5557")
    planner = NearestPointPlanner()
    position_rel_thread = threading.Thread(target=listen_position_rel)
    in_view_thread = threading.Thread(target=listen_in_view)
    position_rel_thread.start()
    in_view_thread.start()


    while True:
        curr_x, curr_y, curr_phi = abs_x, abs_y, abs_phi
        candidates_lock.acquire()
        rel_points = [(x - curr_x, y - curr_y) for x, y in candidates]
        polar_points = [(sqrt(x**2 + y**2), atan2(x, float(y)) - curr_phi) for x, y in rel_points]
        points = np.array([(rho*sin(phi), rho*cos(phi)) for rho, phi in polar_points])
        if points.size:
            dist = np.sum(np.power(points, 2), axis=1)
            target_idx = np.argmin(dist)
            nearest = points[target_idx]
            disp_x, disp_y = nearest
            print(disp_x, disp_y)
        candidates_lock.release()
        time.sleep(1)

        #if points:
    #        target = planner.plan(points)
    #        print("target_rel: ", target)
    #        target_publisher.send(target)

if __name__ == "__main__":
    main()
