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

CURRDIR = os.path.dirname(__file__)

CALIBRATION_FILE = os.path.join(CURRDIR, "runtime/raspicam_v2_m4_calibration.npz")
PROJECTION_FILE = os.path.join(CURRDIR, "runtime/raspicam_v2_m4_backprojection.npz")
COLORMASK_FILE = os.path.join(CURRDIR, "runtime/tennis_ball_color_mask.json")

class RANSACProjector(object):

    def __init__(self, config_file=PROJECTION_FILE):
        self.config = np.load(config_file)
        self.inv_rotation_matrix = self.config["inv_rotation_matrix"]
        self.translation_vector = self.config["translation_vector"]
        self.inv_camera_matrix = self.config["inv_camera_matrix"]
        self.lhs_part = self.inv_rotation_matrix.dot(self.inv_camera_matrix)
        self.rhs = self.inv_rotation_matrix.dot(self.translation_vector)

    def project(self, image_points, height):
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
        blurred = image #cv2.blur(image, self.ksize)
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

class ColorMaskLocater(object):

    def __init__(self, camera):
        self.camera = camera
        self.detector = ColorMaskDetector()
        self.projector = RANSACProjector()

    def locate(self, show=False):
        for image in self.camera.capture():
            image_points, mask = self.detector.detect(image)
            object_points = self.projector.project(image_points, 1/12.)
            if show:
                for (img_x, img_y), (obj_x, obj_y) in zip(image_points, object_points):
                    cv2.circle(image, (img_x, img_y), 3, (0, 0, 0), -1)
                    text = "(%3.1f, %3.1f)" % (obj_x, obj_y)
                    cv2.putText(image, text, (img_x + 5, img_y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0))
                cv2.imshow("camera: analysis feed", image)
                cv2.imshow("camera: color mask", mask)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            if object_points.size:
                yield list(map(tuple, object_points))
            else:
                yield []
