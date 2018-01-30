#!/usr/bin/env python3

"""
Tracking server for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

from tbc_backend.common import Server
from tbc_backend.tracking import MemorylessTracker

def main(port):
    """ main function for server """
    server = Server(args.port)
    onboard_tracker = MemorylessTracker(in_view=False)
    offboard_tracker = MemorylessTracker(in_view=True)
    misses = 0
    for message_type, message in server.listen():
        print("message recieved: ", message_type)

        if message_type == "get_target_rel":
            target = onboard_tracker.get_target_rel()
            if not target:
                if not misses % 2:
                    target = None
                else:
                    target = offboard_tracker.get_target_rel()
                misses += 1
            server.reply(target)
            continue
        else:
            server.reply(True)

        if message_type == "offboard_targets":
            offboard_tracker.update_target_abs(message)
        elif message_type == "onboard_targets":
            onboard_tracker.update_target_rel(message)
        elif message_type == "agent_rel":
            onboard_tracker.update_agent_rel(*message)
            offboard_tracker.update_agent_rel(*message)
        elif message_type == "agent_abs":
            onboard_tracker.update_agent_abs(*message)
            offboard_tracker.update_agent_abs(*message)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--port", dest="port", default="5555", type=str,
                        help="TCP Port to serve on.")
    args = parser.parse_args()

    main(args)
