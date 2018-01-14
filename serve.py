from components.communication import Server
from components.trackers import LatestSentTracker

def main(port):
    server = Server(args.port)
    tracker = LatestSentTracker()
    for request in server.listen():
        print(request)
        if request == "send_target":
            server.reply(tracker.get_target())
        else:
            tracker.update(request)
            server.reply(True)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--port", dest="port", default="5555", type=str,
                        help="TCP Port to serve on.")
    args = parser.parse_args()

    main(args)
