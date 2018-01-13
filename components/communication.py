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
        #self.socket.bind(self.address)
        self.topic = topic
        self.n_sent = 0

    def send(self, message):
        self.socket.connect(self.address)
        message_string = "%s %s %s %s" % (self.topic, time.time(), self.n_sent, message)
        self.socket.send_string(message_string)
        self.n_sent += 1

    def __del__(self):
        self.socket.close()
