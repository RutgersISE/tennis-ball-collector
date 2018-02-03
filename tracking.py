#!/usr/bin/env python3

"""
Tracking and control server for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

import multiprocessing as mp
import numpy as np

from tbc_backend.common import Client, Server
from tbc_backend.tracking import MemorylessTracker
from tbc_backend.control import ArduinoRobot, PointAndShootController

def track(args, conn=None):
    """ target tracking """
    vision_server = Server(args.vision_port)
    robot_client = Client(args.robot_port)
    tracker = MemorylessTracker(in_view=False)
    searcher = MemorylessTracker(in_view=True)
    controller = PointAndShootController(turn_scaling=args.turn_scaling,
                                         forward_scaling=args.forward_scaling,
                                         max_turn_time=args.max_turn_time,
                                         max_forward_time=args.max_forward_time,
                                         buffer_distance=args.buffer_distance)
    old_target = curr_target = 0, 0, False
    for message_type, message in vision_server.listen(autoreply=True):
        try:
            if message_type == "offboard_targets":
                searcher.update_target_abs(message)
            elif message_type == "onboard_targets":
                tracker.update_target_rel(message)
            elif message_type == "agent_rel":
                tracker.update_agent_rel(*message)
                searcher.update_agent_rel(*message)
            elif message_type == "agent_abs":
                tracker.update_agent_abs(*message)
                seacher.update_agent_abs(*message)
            old_target = curr_target
            curr_target = tracker.get_target_rel()
            if not curr_target:
                curr_target = searcher.get_target_rel()
            if not np.isclose(curr_target, old_target, atol=1e-2).all():
                print("curr_target:", curr_target)
                move, delta = controller.control(*target_rel)
        except (KeyboardInterrupt, SystemExit):
            break

def control(args, conn=None):
    robot_server = Server(args.port, args.host)
    robot = ArduinoRobot(args.device, args.baud)
    for message_type, message in robot_server.listen(autoreply=True):
        if message_type != "target_rel":
            continue
            if target_rel is None:
                robot.command(0, 0, .5)
                continue
            else:
                move, delta = controller.control(*target_rel)
                if move:
                    robot.command(*move)
                    client.send("update_agent_rel", delta)
                else:
                    robot.command(0, 0, .5)
        except (KeyboardInterrupt, SystemExit):
            robot.command(0, 0)
            break

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--device", dest="device", default="/dev/ttyACM0", type=str,
                        help="""Unix device path for arduino. Defaults to
                        '/dev/ttyACM0'.""")
    parser.add_argument("--baud", dest="baud", default=38400, type=int,
                        help="Baud rate for arduino. Defaults to '38400'.")
    parser.add_argument("--host", dest="host", default="localhost", type=str,
                        help="""Host for target tracking server. Defaults to
                        'localhost'""")
    parser.add_argument("--vision_port", dest="port", default="5555", type=str,
                        help="Port for target tracking server. Defaults to '5555'.")
    parser.add_argument("--robot_port", dest="port", default="5556", type=str,
                        help="Port for target tracking server. Defaults to '5556'.")
    parser.add_argument("--buffer_distance", dest="buffer_distance", default=0.5,
                        type=float, help="""Extra distance to travel to ensure that
                        ball is collected.""")
    parser.add_argument("--max_turn_time", dest="max_turn_time", default=1.00,
                        type=float, help="""Maximum time to turn without
                        checking the vision system. Defaults to 1.00 second.""")
    parser.add_argument("--max_forward_time", dest="max_forward_time", default=1.00,
                        type=float, help="""Maximum time to move forward without
                        checking the vision system. Defaults to 1.00 second.""")
    parser.add_argument("--turn_scaling", dest="turn_scaling", default=98,
                        type=int, help="""Scaling constant for turn time relative
                        to desired angle.""")
    parser.add_argument("--forward_scaling", dest="forward_scaling", default=115,
                        type=int, help="""Scaling constant for forward move time
                        relative to desired distance.""")
    parser.add_argument("--turn", dest="calibrate_turn", action="store_true",
                        help="Turn 360 degrees to test 'turn_scaling'.")
    parser.add_argument("--forward", dest="calibrate_forward", action="store_true",
                        help="Move 4 feet forward to test 'forward_scaling'.")

    args = parser.parse_args()

    track(args)
