from components.communication import Publisher

def main(args):
    if args.command == "publish":
        publisher = Publisher(args.topic, args.port)
        while True:
            try:
                message = input("%s:%s> " % (args.port, args.topic))
                publisher.send(message)
            except (KeyboardInterrupt):
                return
    elif args.command == "subscribe":
        subscriber = Subscriber(args.topic, args.port)
        while True:
            try:
                print(subscriber.listen())
            except (KeyboardInterrupt):
                return

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("command", type=str)
    parser.add_argument("port", type=str)
    parser.add_argument("topic", type=str)
    args = parser.parse_args()

    main(args)
