import zmq
import time
import ast

class Subscriber(object):

    def __init__(self, topic, port, host="localhost"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.address = "tcp://%s:%s" % (host, port)

    def listen(self):
        self.socket.connect(self.address)
        message_string = self.socket.recv_string()
        topic, timestamp, message_data = message_string.split(" ", 2)
        message = ast.literal_eval(message_data)
        return message

class Publisher(object):

    def __init__(self, topic, port, host="localhost"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.address = "tcp://*:%s" % port
        self.socket.bind(self.address)
        self.topic = topic

    def send(self, message):
        message_string = "%s %s %s" % (self.topic, time.time(), message)
        self.socket.send_string(message_string)
