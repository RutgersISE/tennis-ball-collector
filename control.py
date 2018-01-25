"""
Control frontend for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from components.communication import Client
from components.commanders import ArduinoCommander
from components.controllers import PointAndShootController

def main(args):
    """main function for controller"""
    client = Client(args.port, args.host)
    commander = ArduinoCommander(args.device, args.baud)
    controller = PointAndShootController(max_turn_time=args.max_turn_time,
                                         max_forward_time=args.max_forward_time,
                                         buffer_distance=args.buffer_distance)
    for target_rel in client.listen("send_target")
        if target_rel is None:
            commander.command(0, 0, 1)
            continue
        else:
            move, delta = controller.control(*target_rel)
            if move:
                commander.command(*move)
                client.send("new_position", delta)
            else:
                commander.command(0, 0, 1)
    else:
        commander.command(0, 0)

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
    parser.add_argument("--buffer_distance", dest="buffer_distance", default=1.5,
                        type=float, help="""extra distance to travel to ensure that
                        ball is collected.""")
    parser.add_argument("--max_turn_time", dest="max_turn_time", default=0.25,
                        type=float)
    parser.add_argument("--max_forward_time", dest="max_forward_time", default=1.00,
                        type=float)
    args = parser.parse_args()

    main(args)
