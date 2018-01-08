import zmq 
import sys

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")
