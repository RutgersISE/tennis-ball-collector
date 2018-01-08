import sys
import zmq

port = "5556"
# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:%s" % port)

topic_filter = "rel_discovery"
socket.setsockopt_string(zmq.SUBSCRIBE, topic_filter)

# Process 5 updates
total_value = 0
while True:
    string = socket.recv_string()
    topic, timestamp, message_data = string.split(" ", 2)
    print(timestamp, message_data)
