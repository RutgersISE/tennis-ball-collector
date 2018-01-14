from components.communication import Subscriber, Publisher
from components.commanders import ArduinoCommander
from components.trajectories import PointAndShootTrajector
from components.searchers import RandomSearcher

def main(args):
    subscriber = Subscriber("target_rel", args.sub_port, timeout=500)
    commander = ArduinoCommander(args.device, args.baud)
    searcher = RandomSearcher(args.height, args.width)
    trajector = PointAndShootTrajector()
    while True:
        try:
            message = subscriber.listen()
            if message is None:
                continue
            else:
                x, y = message
            for move, delta in trajector.traject(x, y, args.max_move_time):
                print(move)
                commander.command(*move)
                searcher.update(*delta)
        except (KeyboardInterrupt, SystemExit):
            commander.command(0, 0)
            break

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--device", dest="device", default="/dev/ttyACM0", type=str,
                        help="""Unix device path for arduino. Defaults to
                             '/dev/ttyACM0'.""")
    parser.add_argument("--height", dest="height", default=10, type=int,
                        help="Height of box to constrain robot to. Defaults to '10'.")
    parser.add_argument("--width", dest="width", default=10, type=int,
                        help="Width of box to constraint robot to. Defaults to '10'.")
    parser.add_argument("--baud", dest="baud", default=38400, type=int,
                        help="Baud rate for arduino. Defaults to '38400'.")
    parser.add_argument("--sub_port", dest="sub_port", default="5556", type=str,
                        help="Port for subscribing. Defaults to '5556'.")
    parser.add_argument("--pub_port", dest="pub_port", default="5558", type=str,
                        help="Port for publishing. Defaults to '5558'.")
    parser.add_argument("--max_move_time", dest="max_move_time", default=.75, type=float)
    args = parser.parse_args()

    main(args)
