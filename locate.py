import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("locate_node")

from components.cameras import CalibratedCamera
from components.communication import Publisher
from components.localization import ColorMaskLocater

def main(args):
    publisher = Publisher("in_view", "5556", host=args.host)
    camera = CalibratedCamera(args.device)
    locator = ColorMaskLocater(camera)
    for points in locator.locate(args.show):
        try:
            logger.info("located target, publishing to topic 'in_view'.")
            publisher.send(points)
        except (KeyboardInterrupt, SystemExit):
            break

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--host", dest="host", default="localhost", type=str)
    parser.add_argument("--device", dest="device", default="/dev/video0", type=str)
    parser.add_argument("--show", dest="show", action="store_true")
    args = parser.parse_args()

    main(args)
