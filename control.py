#!/usr/bin/env python3

"""
Control frontend for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from tbc_backend.common import Client
from tbc_backend.control import *

def main(args):
    """main function for controller"""
    client = Client(args.port, args.host)
    robot = ArduinoRobot(args.device, args.baud)
    controller = PointAndShootController(turn_scaling=args.turn_scaling,
                                         forward_scaling=args.forward_scaling,
                                         max_turn_time=args.max_turn_time,
                                         max_forward_time=args.max_forward_time,
                                         buffer_distance=args.buffer_distance)
    if args.calibrate_turn:
        move, delta = controller.control((0, np.pi))
        robot.command(*move)
        robot.command(0, 0, 1)
        return

    if args.calibrate_forward:
        move, delta = controller.control((4, 0))
        robot.command(*move)
        robot.command(0, 0, 1)
        return

    for target_rel in client.listen("get_target_rel"):
        try:
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
            break
    else:
        robot.command(0, 0)

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
    parser.add_argument("--turn", dest="calibrate_turn", action="store_true",
                        help="Turn 360 degrees to test 'turn_scaling'.")
    parser.add_argument("--forward", dest="calibrate_forward", action="store_true",
                        help="Move 4 feet forward to test 'forward_scaling'.")
    args = parser.parse_args()

    main(args)
