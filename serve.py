"""
Central Server for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

import time

from components.communication import Server
from components.trackers import MemorylessTracker

def main(port):
    """ main function for server """
    server = Server(args.port)
    tracker = MemorylessTracker()
    for message_type, message in server.listen():
        if message_type == "send_target":
            target = tracker.get_target()
            #if not target:
            #    target = searcher.get_target()
            server.reply(target)
        elif message_type == "offboard_targets":
            targets = message
            server.reply(True)
            print("recieved %d targets from offboard camera" % len(targets))
            tracker.update_target_abs(targets)
        elif message_type == "onboard_targets":
            targets = message 
            server.reply(True)
            print("recieved %d targets from onboard camera" % len(targets))
            tracker.update_target_rel(targets)
        elif message_type == "rel_agent": 
            agent = message
            server.reply(True)
            tracker.update_agent_rel(*agent)
        else:
            server.reply(False)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--port", dest="port", default="5555", type=str,
                        help="TCP Port to serve on.")
    args = parser.parse_args()

    main(args)
