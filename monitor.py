import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monitor")

import requests
import cv2
import time

from detector import ColorMaskBallDetector

def monitor(device, frames_per_detection=20):
    """ opens camera device and executes the ball detectors """
    logger.info("Opening camera device %s." % device)
    camera = cv2.VideoCapture(device)
    if not camera.isOpened():
        raise RuntimeError("Camera device %s not found." % device)
    logger.info("Initializing ball detector.")
    ball_detector = ColorMaskBallDetector()
    logger.info("Monitoring camera device %s." % device)
    while True:
        try:
            frames = []
            for _ in range(frames_per_detection):
                ret, frame = camera.read()
                if not ret:
                    raise RuntimeError("Stream interrupted.")
                frames.append(frame)
            balls, mask = ball_detector.detect_many(frames)
            if balls:
                logger.info("%s ball(s) detected in frame." % len(balls))
                yield balls, []
            #masked = cv2.bitwise_and(frame, frame, mask=mask)
            #cv2.imshow("masked", masked)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #   break
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt recieved, shutting stream.")
            break
    camera.release()

def transmit(balls, robot, address):
    balls = [{"x" : x, "y" : y, "r" : r} for x, y, r in balls]
    try:
        requests.post(address + "/balls", json=balls)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Server %s/balls cannot be reached." % address)

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Detector for tennis ball collector.")
    parser.add_argument("--device",
                        help="camera device to monitor",
                        default="/dev/video0")
    parser.add_argument("--address",
                        help="address of server to submit detections to",
                        default="http://localhost:5000")
    args = parser.parse_args()

    for balls, robot in monitor(args.device):
        transmit(balls, robot, args.address)
        logger.info("Transmitted detection results to server.")
