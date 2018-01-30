#!/usr/bin/env python3

"""
Vision system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from tbc_backend.common import Client
from tbc_backend.vision import *

def main(args):
    camera = Camera(args.device)
    target_locator = TargetLocator()
    client = Client(args.port, args.host)
    if args.onboard:
        for targets in watch_onboard(camera, target_locator, args.show):
            client.send("onboard_targets", targets)
    else:
        agent_locator = AgentLocator()
        for targets, agent in watch_offboard(camera, target_locator,
                                         agent_locator, args.show):
            client.send("agent_abs", agent)
            client.send("offboard_targets", targets)

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
    parser.add_argument("--onboard", dest="onboard", action="store_true")
    parser.add_argument("--host", dest="host", default="localhost", type=str,
                        help="Hostname for publishing. Defaults to 'localhost'.")
    parser.add_argument("--port", dest="port", default="5555", type=str,
                        help="Port for publishing. Defaults to '5555'.")
    args = parser.parse_args()

    main(args)
