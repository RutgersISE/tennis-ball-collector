#!/usr/bin/env python3
"""
Vision system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

import numpy as np
import cv2
import json
import os
import sys
import time

CURRDIR = os.path.dirname(__file__)
CALIBRATION_FILE = os.path.join(CURRDIR, "runtime/logitech_480p_calibration.npz")
BACKPROJECTION_FILE = os.path.join(CURRDIR, "runtime/logitech_480p_backprojection.npz")
COLORMASK_FILE = os.path.join(CURRDIR, "runtime/tennis_ball_color_mask.json")

class RANSACBackProjector(object):

    def __init__(self, config_file=BACKPROJECTION_FILE):
        self.config = np.load(config_file)
        self.inv_rotation_matrix = self.config["inv_rotation_matrix"]
        self.translation_vector = self.config["translation_vector"]
        self.inv_camera_matrix = self.config["inv_camera_matrix"]
        self.lhs_part = self.inv_rotation_matrix.dot(self.inv_camera_matrix)
        self.rhs = self.inv_rotation_matrix.dot(self.translation_vector)

    def back_project(self, image_points, height):
        if not image_points.size:
            return image_points # if empty, just return another empty
        e = np.ones((image_points.shape[0], 1))
        image_points = np.append(image_points, e, axis=1).T
        lhs = self.lhs_part.dot(image_points)
        s = (height + self.rhs[2, 0])/lhs[2, :]
        object_points = (s*lhs - self.rhs).T[:, 0:2]
        return object_points

class ColorMaskDetector(object):
    def __init__(self, config_file=COLORMASK_FILE):
        with open(config_file) as f:
            self.config = json.loads(f.read())
        self.lower = np.array(self.config["lower"])
        self.upper = np.array(self.config["upper"])
        self.ksize = tuple(self.config["ksize"])
        self.iterations = self.config["iterations"]
        params = cv2.SimpleBlobDetector_Params()
        params.blobColor = 255
        params.filterByColor = True
        params.minArea = self.config["minarea"]
        params.maxArea = np.inf
        params.filterByArea = True
        # shape based parameters should be permissive to allow for failures
        # in the color masking stage. The following lines should only be
        # used if the color mask has been well tuned to a particular background
        params.minCircularity = 0.50
        params.maxCircularity = np.inf
        params.filterByCircularity = True
        params.minInertiaRatio = 0.25
        params.maxInertiaRatio = np.inf
        params.filterByInertia = True
        params.filterByConvexity = False
        self.blob_detector = cv2.SimpleBlobDetector_create(params)

    def make_mask(self, image):
        blurred = cv2.blur(image, self.ksize)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.ksize, iterations=self.iterations)
        return mask

    def get_coords(self, mask):
        keypoints = self.blob_detector.detect(mask)
        image_points = np.array([(int(point.pt[0]), int(point.pt[1])) for point in keypoints])
        return image_points

    def detect(self, image):
        mask = self.make_mask(image)
        image_points = self.get_coords(mask)
        return image_points, mask

    def detect_many(self, images):
        masks = np.stack([self.make_mask(image) for image in images], axis=2)
        levels = np.mean(masks, axis=2)
        mask = np.zeros(images[0].shape[0:2], dtype=np.uint8)
        mask[levels > self.thresh] = 255
        image_points = self.get_coords(mask)
        return image_points, mask

def watch_cv2(device, calibration_file, show=False):
    """ opens camera device and executes the ball detectors """
    calibration = np.load(calibration_file)
    height = calibration["height"]
    width = calibration["width"]
    map_x, map_y = cv2.initUndistortRectifyMap(calibration["camera_matrix"],
                                               calibration["dist_coeffs"],
                                               None,
                                               calibration["new_camera_matrix"],
                                               (width, height),
                                               5)
    camera = cv2.VideoCapture(device)
    if not camera.isOpened():
        raise RuntimeError("Camera device %s not found." % device)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    camera.set(cv2.CAP_PROP_FPS, 20) # high frame rate is not necessary here
    detector = ColorMaskDetector()
    backprojector = RANSACBackProjector()
    while True:
        try:
            average = np.zeros((height, width, 3), dtype=np.float32)
            for i in range(3):
                ret, frame = camera.read()
                cv2.accumulate(frame, average)
            average = (average/3.0).astype(np.uint8)
            image = cv2.remap(average, map_x, map_y, cv2.INTER_LINEAR)
            image_points, mask = detector.detect(image)
            object_points = backprojector.back_project(image_points, 0)
            if show:
                for (img_x, img_y), (obj_x, obj_y) in zip(image_points, object_points):
                    cv2.circle(image, (img_x, img_y), 3, (0, 0, 0), -1)
                    text = "(%3.1f, %3.1f)" % (obj_x, obj_y)
                    cv2.putText(image, text, (img_x + 5, img_y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0))
                cv2.imshow("%s: analysis feed" % device, image)
                cv2.imshow("%s: color mask" % device, mask)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            yield object_points
        except (KeyboardInterrupt, SystemExit):
            break
    camera.release()

def watch_picam(calibration_file, show=False):
    if "picamera" not in sys.modules:
        import picamera
        import picamera.array
    detector = ColorMaskDetector()
    backprojector = RANSACBackProjector()
    with picamera.PiCamera(
        sensor_mode=4, # 1640x1232 with binning,
        framerate=10) as camera:
        camera.resolution = (640, 368)
        camera.video_stabilization = True
        camera.vflip = True
        camera.hflip = True
        time.sleep(2)
        with picamera.array.PiRGBArray(camera, size=camera.resolution) as stream:
            for frame in camera.capture_continuous(stream, format="bgr", use_video_port=True):
                image = stream.array
                image_points, mask = detector.detect(image)
                object_points = backprojector.back_project(image_points, 0)
                if show:
                    for (img_x, img_y), (obj_x, obj_y) in zip(image_points, object_points):
                        cv2.circle(image, (img_x, img_y), 3, (0, 0, 0), -1)
                        text = "(%3.1f, %3.1f)" % (obj_x, obj_y)
                        cv2.putText(image, text, (img_x + 5, img_y - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0))
                    cv2.imshow("picam: analysis feed", image)
                    cv2.imshow("picam: color mask", mask)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                stream.truncate(0)
                yield object_points

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Detector for tennis ball collector.")
    parser.add_argument("--device",
                        help="camera device to monitor",
                        default="/dev/video0")
    parser.add_argument("--calibration_file",
                        help="calibration for camera",
                        default=CALIBRATION_FILE)
    parser.add_argument("--picam", action="store_true")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    if args.picam:
        for object_points in watch_picam(args.calibration_file, args.show):
            if object_points.size:
                print(object_points)
    else:
       for object_points in watch_cv(args.device, args.calibration_file, args.show):
            if object_points.size:
                print(object_points)