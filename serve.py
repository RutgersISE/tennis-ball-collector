from components.communication import Server
from components.trackers import LatestSentTracker
from components.searchers import RandomSearcher

def main(port):
    server = Server(args.port)
    tracker = LatestSentTracker()
    searcher = RandomSearcher(5, 5)
    for message_type, message in server.listen():
        print(message_type, message)
        if message_type == "send_target":
            target = tracker.get_target()
            if not target:
                target = searcher.get_target()
            server.reply(target)
        elif message_type == "new_position":
            server.reply(True)
            tracker.update_position(*message)
            searcher.update_position(*message)
        elif message_type == "new_targets":
            server.reply(True)
            tracker.update_target(message)
        else:
            server.reply(False)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--port", dest="port", default="5555", type=str,
                        help="TCP Port to serve on.")
    args = parser.parse_args()

    main(args)
