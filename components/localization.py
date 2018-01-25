#!/usr/bin/env python3
"""
Vision system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

import json
import os

import cv2
import numpy as np

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

class TargetDetector(object):
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
        params.filterByCircularity = False
        params.minInertiaRatio = 0.25
        params.maxInertiaRatio = np.inf
        params.filterByInertia = False
        params.filterByConvexity = False
        self.blob_detector = cv2.SimpleBlobDetector_create(params)

<<<<<<< HEAD
    def make_mask(self, image):
=======
    def _make_mask(self, image):
>>>>>>> dd7e754942690ebf5179c11e14f1815637513da8
        blurred = cv2.blur(image, self.ksize)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, self.ksize, iterations=self.iterations)
        return mask

    def _get_coords(self, mask):
        x, y, w, h = cv2.boundingRect(mask)
        keypoints = self.blob_detector.detect(mask[y:(y+h), x:(x+w)])
        image_points = np.array([(int(point.pt[0] + x), int(point.pt[1] + y)) for point in keypoints])
        return image_points

    def detect(self, image):
        mask = self._make_mask(image)
        image_points = self._get_coords(mask)
        return image_points, mask

class AgentDetector(object):

    range_1_lower = np.array([  0,  80,  80], np.uint8)
    range_1_upper = np.array([ 10, 255, 255], np.uint8)
    range_2_lower = np.array([170,  80,  80], np.uint8)
    range_2_upper = np.array([180, 255, 255], np.uint8)

    def __init__(self):
        pass

    def _make_mask(self, image, lower, upper):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.dilate(mask, np.ones((3, 3)))
        return mask

    def _get_coords(self, mask):
        _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour = max(contours, key = cv2.contourArea)
        mask = np.zeros_like(mask)
        cv2.fillPoly(mask, [contour], (255, 255, 255))
        points = np.squeeze(cv2.findNonZero(mask))
        centroid = np.mean(points, axis=0)
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        # TODO sloppy
        lines = [(box[0], box[-1])]
        for a, b in zip(box[1:], box[:-1]):
            lines.append((a, b))
        lines = np.array(lines)
        centers = np.mean(lines, axis=1).astype(int)
        dist = np.sum(np.power(centers - centroid, 2), axis=1)
        front = np.argmax(dist)
        dist = np.sum(np.power(centers - centers[front], 2), axis=1)
        rear = np.argmax(dist)
        return centers[front], centers[rear], mask

    def detect(self, image):
        mask_1 = self._make_mask(image, self.range_1_lower, self.range_1_upper)
        mask_2 = self._make_mask(image, self.range_2_lower, self.range_2_upper)
        mask = cv2.bitwise_or(mask_1, mask_2)
        front, rear, mask = self._get_coords(mask)
        return front, rear, mask

class TargetLocator(object):

    def __init__(self):
        self.detector = TargetDetector()
        self.projector = RANSACProjector()

    def locate(self, image, display_image=None):
        image_points, mask = self.detector.detect(image)
        object_points = self.projector.project(image_points, 1/12.)
        if display_image is not None:
            for (img_x, img_y), (obj_x, obj_y) in zip(image_points, object_points):
                cv2.circle(display_image, (img_x, img_y), 3, (0, 0, 0), -1)
                text = "(%3.1f, %3.1f)" % (obj_x, obj_y)
                cv2.putText(display_image, text, (img_x + 5, img_y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0))
        if object_points.size:
            return list(map(tuple, object_points)), display_image
        else:
            return [], display_image

class AgentLocator(object):

    def __init__(self):
        self.detector = AgentDetector()
        self.projector = RANSACProjector()

    def locate(self, image, display_image=None):
        image_front, image_rear, mask = self.detector.detect(image)
        object_front = self.projector.project(np.array([image_front]), 0.5)
        object_rear = self.projector.project(np.array([image_rear]), 0.5)
        object_delta = object_front - object_rear
        x, y = tuple(object_delta[0])
        phi = np.arctan2(y, x)
        if display_image is not None:
            cv2.arrowedLine(display_image, tuple(image_rear), tuple(image_front),
                            (0, 0, 0), 3)
        return (x, y, phi), display_image

def watch(camera, target_locator, agent_locator, show=False):
    for image in camera.capture():
        targets, display_image = target_locator.locate(image, image)
        agent, display_image = agent_locator.locate(image, display_image)
        if show:
            cv2.imshow("analysis_feed", display_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        yield targets, agent
    #if show:
    #    for (img_x, img_y), (obj_x, obj_y) in zip(image_points, object_points):
    #        cv2.circle(image, (img_x, img_y), 3, (0, 0, 0), -1)
    #        text = "(%3.1f, %3.1f)" % (obj_x, obj_y)
    #        cv2.putText(image, text, (img_x + 5, img_y - 5),
    #                    cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0))
    #    cv2.imshow("camera: analysis feed", image)
    #    cv2.imshow("camera: color mask", mask)
