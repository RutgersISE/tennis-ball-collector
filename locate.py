import os

from components.communication import Publisher
from components.localization import ColorMaskLocater
if os.uname()[4][:3] == 'arm':
    from components.cameras import CalibratadPicamera as Camera
else:
    from components.cameras import CalibratedCamera as Camera

def main(args):
    camera = Camera(args.device)
    locator = ColorMaskLocater(camera)
    if args.nearest:
        publisher = Publisher("target_rel", args.pub_port, args.pub_host)
        for point in locator.locate_nearest(args.show):
            publisher.send(point)
    else:
        publisher = Publisher("onboard_view", args.pub_port, args.pub_host)
        for points in locator.locate_all(args.show):
            publisher.send(points)

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--device", dest="device", default="/dev/video0", type=str,
                        help="Unix device path for camera. Defaults to '/dev/video0'.")
    parser.add_argument("--show", dest="show", action="store_true",
                        help="""Display camera feed with locations. This requires
                        significant CPU, should only be active for
                        troubleshooting.""")
    parser.add_argument("--nearest", dest="nearest", action="store_true",
                        help="""Publish nearest point directly to 'target_rel' topic.
                        This must be activated if running in single camera locate
                        and control mode.""")
    parser.add_argument("--pub_host", dest="pub_host", default="localhost", type=str,
                        help="Hostname for publishing. Defaults to 'localhost'.")
    parser.add_argument("--pub_port", dest="pub_port", default="5556", type=str,
                        help="Port for publishing. Defaults to '5556'.")

    args = parser.parse_args()

    main(args)
