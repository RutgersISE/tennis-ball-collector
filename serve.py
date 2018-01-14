from components.communication import Server

def main(port):
    server = Server(args.port)
    for request in server.listen(autoreply=True):
        print(request)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--port", dest="port", default="5555", type=str,
                        help="TCP Port to serve on.")
    args = parser.parse_args()

    main(args)
