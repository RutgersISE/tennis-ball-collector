"""
Communication backend for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

import ast
import time

import zmq

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
                _, message_type, message_data = string.split(" ", 2)
                try:
                    message = ast.literal_eval(message_data)
                except ValueError:
                    message = message_data
                if autoreply:
                    self.reply(True)
                yield message_type, message
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

    def request(self, message_type, req_message=None):
        self.socket.connect(self.address)
        req_string = "%s %s %s" % (time.time(), message_type, req_message)
        self.socket.send_string(req_string)
        rep_string = self.socket.recv_string()
        _, data = rep_string.split(" ", 1)
        message = ast.literal_eval(data)
        return message

    def send(self, message_type, req_message=None):
        self.request(message_type, req_message)

    def listen(self, message_type):
        while True:
            try:
                yield self.send(message_type)
            except (KeyboardInterrupt, SystemExit):
                return
