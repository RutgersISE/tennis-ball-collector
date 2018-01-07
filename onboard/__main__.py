import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from argparse import ArgumentParser

from vision import CalibratedCamera, ColorMaskLocater
from control import ArduinoCommander, PointAndShootPlanner

parser = ArgumentParser(description="Tennis ball collector.")
parser.add_argument("--port",  dest="port", type=str, default="/dev/ttyACM0",
                    help="port address of motor controller.")
parser.add_argument("--baud", dest="baud", type=int, default=9600,
                    help="baud rate of motor controller.")
parser.add_argument("--device",
                    help="camera device to monitor",
                    default="/dev/video0")
parser.add_argument("--calibration_file",
                    help="calibration for camera",
                    default="onboard/runtime/logitech_480p_calibration.npz")
args = parser.parse_args()

logger.info("initializing onboard camera")
camera = CalibratedCamera(args.device, args.calibration_file)
logger.info("initializing onboard commander")
commander = ArduinoCommander(args.port, args.baud)
logger.info("initializing target locater")
locater = ColorMaskLocater()
logger.info("initializing motion planner")
planner = PointAndShootPlanner()

logger.info("beginning image capture")
for image in camera.capture():
    try:
        object_points = locater.locate(image, True)
        if not object_points.size:
            commander.command(0, 0)
            continue
        logger.info("%d targets detected" % object_points.shape[0])
        left_speed, right_speed, _ = planner.plan(object_points)
        logger.info("moving with speed (%s, %s)" % (left_speed, right_speed))
        commander.command(left_speed, right_speed)
    except (KeyboardInterrupt, SystemExit):
        commander.command(0, 0)
        break
