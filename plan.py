import threading
import time
from math import cos, sin, atan2, sqrt

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
        abs_phi += disp_phi
        abs_x += disp_rho*cos(abs_phi)
        abs_y += disp_rho*sin(abs_phi)
        position_lock.release()

candidates_lock = threading.Lock()
candidates = set()

def listen_in_view():
    global abs_x, abs_y, abs_phi
    in_view_subscriber = Subscriber("in_view", "5556")
    while True:
        rel_points = in_view_subscriber.listen()
        polar_points = [(sqrt(x**2 + y**2), atan2(x, y)) for x, y in rel_points] 
        curr_x, curr_y, curr_phi = abs_x, abs_y, abs_phi
        abs_points = [(curr_x + rho*sin(curr_phi + phi), curr_y + rho*cos(curr_phi + phi)) for rho, phi in polar_points]      
        abs_points = [(round(x, 1), round(y, 1)) for x, y in abs_points]
        candidates_lock.acquire()
        candidates.update(abs_points)
        candidates_lock.release()

def main():
    target_publisher = Publisher("target_rel", "5557")
    planner = NearestPointPlanner()
    position_rel_thread = threading.Thread(target=listen_position_rel)
    in_view_thread = threading.Thread(target=listen_in_view)
    position_rel_thread.start()
    in_view_thread.start()

    while True:
        curr_x, curr_y, curr_phi = abs_x, abs_y, abs_phi
        rel_points = [(x - curr_x, y - curr_y) for x, y in candidates]
        polar_points = [(sqrt(x**2 + y**2), atan2(x, float(y)) - curr_phi) for x, y in rel_points]
        points = [(rho*sin(phi), rho*cos(phi)) for rho, phi in polar_points]
        if points:
            target = planner.plan(points)
            print("target_rel: ", target)
            target_publisher.send(target)
        time.sleep(.25)

if __name__ == "__main__":
    main()
