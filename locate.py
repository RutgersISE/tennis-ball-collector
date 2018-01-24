import os

from components.communication import Client
from components.localization import TargetLocator, AgentLocator, watch
if os.uname()[4][:3] == 'arm':
    from components.cameras import CalibratedPicamera as Camera
else:
    from components.cameras import CalibratedCamera as Camera

def main(args):
    camera = Camera(args.device)
    target_locator = TargetLocator()
    agent_locator = AgentLocator()
    client = Client(args.port, args.host)
    for targets, agent in watch(camera, target_locator, agent_locator, args.show):
        client.send("abs_state", (targets, agent))

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
    parser.add_argument("--host", dest="host", default="localhost", type=str,
                        help="Hostname for publishing. Defaults to 'localhost'.")
    parser.add_argument("--port", dest="port", default="5555", type=str,
                        help="Port for publishing. Defaults to '5555'.")
    args = parser.parse_args()

    main(args)
