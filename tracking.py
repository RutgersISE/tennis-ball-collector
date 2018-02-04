#!/usr/bin/env python3

"""
Tracking and control server for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

import numpy as np

from tbc_backend.common import Client, Server
from tbc_backend.tracking import MemorylessTracker
from tbc_backend.control import ArduinoRobot, PointAndShootController

def main(args):
    """ target tracking """
    track_server = Server(args.track_port)
    robot_client = Client(args.robot_port)
    tracker = MemorylessTracker(in_view=False)
    searcher = MemorylessTracker(in_view=True)
    controller = PointAndShootController(turn_scaling=args.turn_scaling,
                                         forward_scaling=args.forward_scaling,
                                         max_turn_time=args.max_turn_time,
                                         max_forward_time=args.max_forward_time,
                                         buffer_distance=args.buffer_distance)
    change = False
    for message_type, message in track_server.listen(autoreply=True):
        if message_type == "offboard_targets":
            searcher.update_target_abs(message)
            change = True
        elif message_type == "onboard_targets":
            tracker.update_target_rel(message)
            change = True
        elif message_type == "agent_rel":
            tracker.update_agent_rel(*message)
            searcher.update_agent_rel(*message)
        elif message_type == "agent_abs":
            tracker.update_agent_abs(*message)
            searcher.update_agent_abs(*message)
        if change:
            target = tracker.get_target_rel()
            if not target:
                target = searcher.get_target_rel()
            print("curr_target:", target)
            move, delta = controller.control(*target)
            robot_client.send("command", (move, delta))
            change = False

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--host", dest="host", default="localhost", type=str,
                        help="""Host for target tracking server. Defaults to
                        'localhost'""")
    parser.add_argument("--track_port", dest="track_port", default="5555", type=str,
                        help="Port for target tracking server. Defaults to '5555'.")
    parser.add_argument("--robot_port", dest="robot_port", default="5556", type=str,
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
    args = parser.parse_args()

    main(args)
