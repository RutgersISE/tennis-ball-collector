#!/usr/bin/env python3

"""
Tracking and control server for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from time import time, sleep
from threading import Thread

from tbc_backend.common import Client, Server
from tbc_backend.tracking import ThreadsafeTracker
from tbc_backend.control import ArduinoRobot, PointAndShootController

def listen(server, onboard, offboard):
    for message_type, message in server.listen(autoreply=True):
        #print("message:", message_type)
        if message_type == "offboard_targets":
            targets = message
            offboard.targets_abs = targets
        elif message_type == "onboard_targets":
            targets = message
            onboard.targets_rel = targets
        elif message_type == "agent_abs":
            x, y, phi = message
            offboard.agent_abs = x, y, phi

def move(controller, driver, tracker, searcher, wait=0.5, update=0.5):
    while True:
        target = tracker.targets_rel
        if target:
            move, delta = controller.control(*target)
            driver.command(*move)
            _, _, move_time, _ = move
            sleep(min(update, move_time))
        else:
            sleep(wait)
            driver.stop()
            sleep(wait)
            target = searcher.targets_rel
            if not target:
                continue
            print(target)
            move, delta = controller.control(*target)
            driver.command(*move)
            _, _, move_time, _ = move
            while move_time > update:
                if tracker.targets_rel:
                    break
                wait_time = min(update, move_time)
                move_time -= wait_time
                sleep(wait_time)
            else:
                sleep(move_time)
    driver.stop()

def main(args):
    track_server = Server(args.port)
    driver = ArduinoRobot(args.device, args.baud)
    tracker = ThreadsafeTracker(in_view=False)
    searcher = ThreadsafeTracker(in_view=True)
    controller = PointAndShootController(turn_scaling=args.turn_scaling,
                                         forward_scaling=args.forward_scaling,
                                         max_turn_time=args.max_turn_time,
                                         max_forward_time=args.max_forward_time,
                                         buffer_distance=args.buffer_distance)
    listen_thread = Thread(target=listen,
                           args=(track_server, tracker, searcher))
    move_thread = Thread(target=move, 
                         args=(controller, driver, tracker, searcher))
    listen_thread.start()
    move_thread.start()
    listen_thread.join()
    move_thread.join()


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
    parser.add_argument("--port", dest="port", default="5555", type=str,
                        help="Port for target tracking server. Defaults to '5555'.")
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
