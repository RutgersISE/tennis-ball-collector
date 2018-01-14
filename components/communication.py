import zmq
import time
import ast

class Subscriber(object):

    def __init__(self, topic, port, timeout=None, host="*"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.address = "tcp://%s:%s" % (host, port)
        self.socket.bind(self.address)
        if timeout is not None:
            self.socket.RCVTIMEO = timeout
        self.messages_seen = set()

    def listen(self):
        try:
            message_string = self.socket.recv_string()
            if message_string not in self.messages_seen:
                self.messages_seen.add(message_string)
            else:
                # messages are sometimes duplicated
                return None
            topic, timestamp, n_sent, message_data = message_string.split(" ", 3)
            message = ast.literal_eval(message_data)
            return message
        except zmq.error.Again:
            return None

    def __del__(self):
        self.socket.close()

class Publisher(object):

    def __init__(self, topic, port, host="localhost"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.address = "tcp://%s:%s" % (host, port)
        self.socket.bind(self.address)
        self.topic = topic
        self.n_sent = 0

    def send(self, message):
        message_string = "%s %s %s %s" % (self.topic, time.time(), self.n_sent, message)
        self.socket.send_string(message_string)
        self.n_sent += 1

    def __del__(self):
        self.socket.close()

class Server(object):

    def __init__(self, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.address = "tcp://*:%s" % port
        self.socket.bind(self.address)
        self.strings_seen = set()

    def listen(self, autoreply=False):
        while True:
            try:
                string = self.socket.recv_string()
                if string in self.strings_seen:
                    self.reply(False)
                    continue
                self.strings_seen.add(string)
                _, data = string.split(" ", 1)
                try:
                    message = ast.literal_eval(data)
                except ValueError:
                    message = data
                if autoreply:
                    self.reply(True)
                yield message
            except (KeyboardInterrupt, SystemExit):
                return

    def reply(self, message):
        string = "%s %s" % (time.time(), message)
        self.socket.send_string(string)

class Client(object):

    def __init__(self, port, host="localhost"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.address = "tcp://%s:%s" % (host, port)

    def request(self, req_message):
        self.socket.connect(self.address)
        req_string = "%s %s" % (time.time(), req_message)
        self.socket.send_string(req_string)
        rep_string = self.socket.recv_string()
        _, data = rep_string.split(" ", 1)
        message = ast.literal_eval(data)
        return message

    def send(self, message):
        self.request(message)
