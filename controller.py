from serial import Serial
import sys
import time
from math import atan, sqrt, pow
import numpy as np
import sqlite3

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x) - np.pi/2 # 90 degree correction for headings
    return(rho, phi)

class Controller(object):
    forward_move_calibration = 1.31855
    turning_move_calibration = 1.39195

    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.arduino = Serial(self.port, self.baud)
        self.curr_x = self.curr_y = self.curr_phi = 0

    def set_position(self, x, y, phi):
        logger.info("updating position to be x=%s y=%s phi=%s" % (x, y, phi))
        self.curr_x, self.curr_y, self.curr_phi = x, y, phi

    def reconfigure(self, forward_move_calibration=None, turning_move_calibration=None):
        if forward_move_calibration:
            self.forward_move_calibration = forward_move_calibration
            logger.info("reconfigured forward_move_calibration=%s" % forward_move_calibration) 
        if turning_move_calibration:
            self.turning_move_calibration = turning_move_calibration
            logger.info("reconfigured turning_move_calibration=%s" % turning_move_calibration) 
  
    def send(self, left_speed, right_speed):
        message = "%d %d\n" % (left_speed, right_speed)
        self.arduino.flushInput()
        self.arduino.flushOutput()
        self.arduino.flush()
        self.arduino.write(message.encode())
    
    def move(self, left_speed, right_speed, move_time):
        self.send(left_speed, right_speed)
    #    time.sleep(move_time)
    #    self.send(0, 0)

    def move_to(self, x, y, speed=50):
        """ performs simple two phase moves: rotate and move forward. """
        x_disp = x - self.curr_x 
        y_disp = y - self.curr_y
        logger.info("recieved command x_disp=%s, y_disp=%s" % (x_disp, y_disp))
        rho_disp, phi = cart2pol(x_disp, y_disp)
        phi_disp = phi - self.curr_phi
        self.curr_x, self.curr_y, self.curr_phi = x, y, phi
        if not np.isclose(phi_disp, 0, atol=1e-1):
            turning_move_time = self.turning_move_calibration*abs(phi_disp)
            logger.info("executing turning move phi=%s radians, time=%s seconds" % (phi_disp, turning_move_time))
            if phi_disp < 0:
                self.move(-speed, speed, turning_move_time)
            else:
                self.move(speed, -speed, turning_move_time)
        if not np.isclose(rho_disp, 0):
            forward_move_time = self.forward_move_calibration*abs(rho_disp)
            logger.info("executing forward move rho=%s feet, time=%s seconds" % (rho_disp, forward_move_time))
            self.move(speed, speed, forward_move_time)
        return x, y, phi

if __name__ == "__main__": 
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Listen for commands to execute on robot.")
    parser.add_argument("--port",  dest="port", type=str, default="/dev/ttyACM0",
                        help="port address of motor controller.")
    parser.add_argument("--baud", dest="baud", type=int, default=9600,
                        help="baud rate of motor controller.")
    args = parser.parse_args()

    controller = Controller(args.port, args.baud)
    controller.move_to(0, 10)
