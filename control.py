from components.communication import Subscriber, Publisher
from components.commanders import ArduinoCommander
from components.trajectories import PointAndShootTrajector
from components.searchers import RandomSearcher

def main(args):
    target_subscriber = Subscriber("target_rel", args.sub_port, timeout=500)
    commander = ArduinoCommander(args.device, args.baud)
    searcher = RandomSearcher(args.height, args.width)
    trajector = PointAndShootTrajector()
    while True:
        disp = target_subscriber.listen()
        if disp is None:
            disp = searcher.search()
        l_speed, r_speed, move_time, disp_rho, disp_phi, stop = trajector.traject(*disp)
        if move_time == 0:
            commander.command(0, 0)
        else:
            commander.command(l_speed, r_speed, move_time, stop)
            searcher.update(disp_rho, disp_phi)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--device", dest="device", default="/dev/ttyACM0", type=str,
                        help="Unix device path for arduino. Defaults to '/dev/ttyACM0'.")
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
    args = parser.parse_args()

    main(args)
