import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("command_node")

from components.communication import Subscriber, Publisher
from components.commanders import ArduinoCommander
from components.trajectories import PointAndShootTrajector

def main(args):
    target_subscriber = Subscriber("target_rel", "5557")
    position_publisher = Publisher("position_rel", "5558")
    commander = ArduinoCommander(args.device, args.baud)
    trajector = PointAndShootTrajector()
    while True:
        try:
            logger.info("listening to topic 'target_rel'.")
            disp_x, disp_y = target_subscriber.listen()
            logger.info("message recieved, preparing instructions.")
            l_speed, r_speed, move_time, disp_rho, disp_phi = trajector.traject(disp_x, disp_y)
            if move_time == 0:
                commander.command(0, 0)
                continue
            logger.debug((l_speed, r_speed, move_time, disp_rho, disp_phi))
            commander.command(l_speed, r_speed, move_time)
            logger.info("changed position, publishing to topic 'position_rel'.")
            position_publisher.send((disp_rho, disp_phi))
            logger.info("executed instructions.")
        except (KeyboardInterrupt, SystemExit):
            break

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--host", dest="host", default="localhost", type=str)
    parser.add_argument("--device", dest="device", default="/dev/ttyACM0", type=str)
    parser.add_argument("--baud", dest="baud", default=38400, type=int)
    args = parser.parse_args()

    main(args)
