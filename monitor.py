import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monitor")

import requests
import cv2
import time

from detector import ColorMaskBallDetector

def monitor(device):
    """ opens camera device and executes the ball detectors """
    logger.info("Opening camera device %s." % device)
    camera = cv2.VideoCapture(device)
    if not camera.isOpened():
        raise RuntimeError("Camera device %s not found." % device)
    logger.info("Initializing ball detector.")
    ball_detector = ColorMaskBallDetector()
    logger.info("Monitoring camera device %s." % device)
    while True:
        frames = []
        for i in range(20):
            ret, frame = camera.read()
            if not ret:
                raise RuntimeError("Stream interrupted.")
            frames.append(frame)
        balls, masked = ball_detector.detect_many(frames)
        if balls:
            logger.info("%s ball(s) detected in frame." % len(balls))
            yield balls
#        cv2.imshow("masked", masked)
#        if cv2.waitKey(1) & 0xFF == ord('q'):
#            break
    camera.release()

if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    for i, balls in enumerate(monitor(0)):
        continue
