from argparse import ArgumentParser

from vision import watch
from control import move

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
                    default="nav_computer/runtime/logitech_480p_calibration.npz")
parser.add_argument("--show", action="store_true")
args = parser.parse_args()

m = move(args.port, args.baud)
m.send(None)
for object_points in watch(args.device, args.calibration_file, args.show):
    m.send(object_points)
