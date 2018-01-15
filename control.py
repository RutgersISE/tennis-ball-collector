from components.communication import Client
from components.commanders import ArduinoCommander
from components.trajectories import PointAndShootTrajector

def main(args):
    client = Client(args.port, args.host)
    commander = ArduinoCommander(args.device, args.baud)
    trajector = PointAndShootTrajector(max_turn_time=args.max_turn_time,
                                       max_forward_time=args.max_forward_time,
                                       buffer_distance=args.buffer_distance)
    while True:
        try:
            target_rel = client.request("send_target")
            if target_rel is None:
                commander.command(0, 0, 1)
                continue
            else:
                rho, phi, finish = target_rel
                move, delta = trajector.traject(rho, phi, finish)
                if move:
                    commander.command(*move)
                    client.send("new_position", delta)
                else:
                    commander.command(0, 0, 1)
        except (KeyboardInterrupt, SystemExit):
            commander.command(0, 0)
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
