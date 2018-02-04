#!/usr/bin/env python3
"""
controls for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from tbc_backend.common import Server
from tbc_backend.control import ArduinoRobot

def main(args):
    server = Server(args.robot_port)
    driver = ArduinoRobot(args.device, args.baud)
    for _, (move, _) in server.listen(autoreply=True):
        driver.command(*move)
    driver.stop()

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--device", dest="device", default="/dev/ttyACM0", type=str,
                        help="""Unix device path for arduino. Defaults to
                        '/dev/ttyACM0'.""")
    parser.add_argument("--baud", dest="baud", default=38400, type=int,
                        help="Baud rate for arduino. Defaults to '38400'.")
    parser.add_argument("--host", dest="host", default="localhost", type=str,
                        help="""Host for robot control server. Defaults to
                        'localhost'""")
    parser.add_argument("--robot_port", dest="robot_port", default="5556", type=str,
                        help="Port for robot control server. Defaults to '5556'.")

    args = parser.parse_args()

    main(args)
