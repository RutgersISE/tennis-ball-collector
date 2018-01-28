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
    onboard_tracker = MemorylessTracker()
    offboard_tracker = MemorylessTracker()
    for message_type, message in server.listen():
        print("message recieved: ", message_type)
        if message_type == "get_target_rel":
            target = onboard_tracker.get_target_rel()
            if not target:
                target = offboard_tracker.get_target_rel()
            server.reply(target)
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
