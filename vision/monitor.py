import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monitor")

import numpy as np
import cv2
import time

from localization import ColorMaskDetector, RANSACBackProjector

def watch_camera(device, calibration_file):
    """ opens camera device and executes the ball detectors """
    logger.info("Calibrating camera.")
    calibration = np.load(calibration_file)
    camera_matrix = calibration["camera_matrix"]
    dist_coeffs = calibration["dist_coeffs"]
    new_camera_matrix = calibration["new_camera_matrix"]
    height = calibration["height"]
    width = calibration["width"]
    map_x, map_y = cv2.initUndistortRectifyMap(camera_matrix, dist_coeffs, None,
                                               new_camera_matrix, (width, height), 5)
    logger.info("Opening camera device %s." % device)
    camera = cv2.VideoCapture(device)
    if not camera.isOpened():
        raise RuntimeError("Camera device %s not found." % device)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    camera.set(cv2.CAP_PROP_FPS, 5)
    _, average = camera.read()
    average = np.float32(average)
    logger.info("Initializing ball detector.")
    detector = ColorMaskDetector()
    logger.info("Monitoring camera device %s." % device)
    while True:
        try:
            ret, frame = camera.read()
            frame = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR)
            cv2.accumulateWeighted(frame, average, .25)
            smoothed = cv2.convertScaleAbs(average)
            image_points, mask = detector.detect(smoothed)
            cv2.imshow("smoothed feed", smoothed)
            if cv2.waitKey(1) & 0xFF == ord('q'):
               break
            if image_points.size:
                yield image_points
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt recieved, shutting stream.")
            break
    camera.release()

def main(device, calibration_file):
    backprojector = RANSACBackProjector()
    for image_points in watch_camera(device, calibration_file):
        object_points = backprojector.back_project(image_points, 0)
        object_x = object_points[:, 0]
        object_y = object_points[:, 1]
        print(object_points)


if __name__ == "__main__":
    from argparse import ArgumentParser
    import matplotlib.pyplot as plt
    parser = ArgumentParser(description="Detector for tennis ball collector.")
    parser.add_argument("--device",
                        help="camera device to monitor",
                        default="/dev/video0")
    parser.add_argument("--calibration_file",
                        help="calibration for camera",
                        default="runtime/logitech_480p_calibration.npz")
    args = parser.parse_args()

    main(args.device, args.calibration_file)
