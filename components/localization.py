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

    def _make_mask(self, image):
        blurred = cv2.blur(image, self.ksize)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, self.ksize, iterations=self.iterations)
        return mask

    def _get_coords(self, mask):
        x, y, w, h = cv2.boundingRect(mask)
        if not mask[y:(y + h), x:(x + w)].size:
            return np.empty((2, 0), dtype=np.float32)
        keypoints = self.blob_detector.detect(mask[y:(y+h), x:(x+w)])
        image_points = np.array([(int(point.pt[0] + x), int(point.pt[1] + y)) for point in keypoints])
        return image_points

    def detect(self, image):
        mask = self._make_mask(image)
        image_points = self._get_coords(mask)
        return image_points, mask

class AgentDetector(object):

    def __init__(self):
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
        marker_0 = cv2.aruco.drawMarker(self.dictionary, 0, 1000)
        marker_1 = cv2.aruco.drawMarker(self.dictionary, 1, 1000)
        cv2.imwrite("marker_0.jpg", marker_0)
        cv2.imwrite("marker_1.jpg", marker_1)

    def _make_mask(self, image, lower, upper):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.dilate(mask, np.ones((3, 3)))
        return mask

    def _get_roi(self, mask):
        x, y, w, h = cv2.boundingRect(mask)
        if not mask[y:(y + h), x:(x + w)].size:
            return None
        return x, y, w, h       

    def _get_coords(self, image):
        corners, ids, _ = cv2.aruco.detectMarkers(image, self.dictionary)
        if ids is None:
            return None, None
        corners = [c for c, i in zip(corners, ids) if i == 0]
        if not corners:
            return None, None
        selected = np.squeeze(corners[0])
        front = np.round(np.mean(selected[0:2], axis=0))
        rear = np.round(np.mean(selected[2:4], axis=0))
        return front, rear

    def detect(self, image):
        front_left, front_right = self._get_coords(image)
        return front_left, front_right

class TargetLocator(object):

    def __init__(self):
        self.detector = TargetDetector()
        self.projector = RANSACProjector()

    def locate(self, image, display_image=None):
        image_points, mask = self.detector.detect(image)
        object_points = self.projector.project(image_points, 1/12.)
        if display_image is not None and object_points.size:
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
        image_front, image_rear = self.detector.detect(image)
        if image_front is None:
            return (None, None, None), display_image
        object_front = self.projector.project(np.array([image_front]), 0.5)
        object_rear = self.projector.project(np.array([image_rear]), 0.5)
        object_delta = object_front - object_rear
        delta_x, delta_y = tuple(object_delta[0])
        x, y = tuple(object_front[0])
        phi = np.arctan2(delta_y, delta_x)
        x += .5*np.cos(phi)
        y += .5*np.sin(phi)
        if display_image is not None:
            cv2.arrowedLine(display_image, tuple(image_rear), tuple(image_front),
                            (0, 0, 0), 3)
        return (x, y, phi), display_image

def watch_offboard(camera, target_locator, agent_locator, show=False):
    while True:
        try:
            image = camera.capture_single()
            targets, display_image = target_locator.locate(image, image.copy())
            targets = [(x, y) for x, y in targets if ((0 < x < 8) and (0 < y < 8))]
            agent, display_image = agent_locator.locate(image, display_image)
            if show:
                cv2.imwrite("analysis_feed.jpg", display_image)
                #cv2.imshow("analysis_feed", display_image)
                #if cv2.waitKey(1) & 0xFF == ord('q'):
                #    break
            yield targets, agent
        except (KeyboardInterrupt, SystemExit):
            return

def watch_onboard(camera, target_locator, show=False):
    for image in camera.capture():
        targets, display_image = target_locator.locate(image, image.copy())
        if show:
            cv2.imshow("analysis_feed", display_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        yield targets
