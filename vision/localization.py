import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monitor")

import numpy as np
import cv2
import json

BACKPROJECTION_FILE = "runtime/logitech_480p_backprojection.npz"
COLORMASK_FILE = "runtime/tennis_ball_color_mask.json"

class RANSACBackProjector(object):

    def __init__(self, config_file=BACKPROJECTION_FILE):
        self.config = np.load(config_file)
        self.inv_rotation_matrix = self.config["inv_rotation_matrix"]
        self.translation_vector = self.config["translation_vector"]
        self.inv_camera_matrix = self.config["inv_camera_matrix"]
        self.lhs_part = self.inv_rotation_matrix.dot(self.inv_camera_matrix)
        self.rhs = self.inv_rotation_matrix.dot(self.translation_vector)

    def back_project(self, image_points, height):
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
