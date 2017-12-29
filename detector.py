import numpy as np
import cv2
from collections import namedtuple

Ball = namedtuple("Ball", "x y r")

YLOWER = np.array([20, 50, 50])
YUPPER = np.array([50, 255, 255])
MINAREA = 50
KSIZE = (5, 5)
ITER = 5
THRESHOLD = .90

class ColorMaskBallDetector(object):
    def __init__(self, lower=YLOWER, upper=YUPPER, thresh=THRESHOLD, area=MINAREA, ksize=KSIZE, iterations=ITER):
        self.lower = lower
        self.upper = upper
        self.thresh = thresh
        self.ksize = ksize
        self.iterations = iterations
        params = cv2.SimpleBlobDetector_Params()
        params.blobColor = 255
        params.filterByColor = True
        params.minArea = area
        params.maxArea = np.inf
        params.filterByArea = True
        # shape based parameters should be permissive to allow for failures
        # in the color masking stage. The following lines should only be
        # used if the color mask has been well tuned to a particular background
        params.minCircularity = 0.5
        params.maxCircularity = np.inf
        params.filterByCircularity = False
        params.minInertiaRatio = 0.25
        params.maxInertiaRatio = np.inf
        params.filterByInertia = False
        self.blob_detector = cv2.SimpleBlobDetector_create(params)

    def make_mask(self, image):
        blurred = cv2.blur(image, self.ksize)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.ksize, iterations=self.iterations)
        return mask

    def get_coords(self, mask):
        keypoints = self.blob_detector.detect(mask)
        coords = [Ball(int(point.pt[0]), int(point.pt[1]), int(point.size/2)) for point in keypoints]
        return coords

    def detect(self, image):
        mask = self.make_mask(image)
        coords = self.get_coords(mask)
        return coords, mask

    def detect_many(self, images):
        masks = np.stack([self.make_mask(image) for image in images], axis=2)
        levels = np.mean(masks, axis=2)
        mask = np.zeros(images[0].shape[0:2], dtype=np.uint8)
        mask[levels > self.thresh] = 255
        coords = self.get_coords(mask)
        return coords, mask

if __name__ == "__main__":
    from glob import glob
    example_paths = "../images/multiple_balls/*.jpg"
    ball_detector = ColorMaskBallDetector()
    for src_path in glob(example_paths):
        image = cv2.imread(src_path)
        balls, masked = ball_detector.detect(image)
        for x, y, r in balls:
            cv2.circle(masked, (x, y), r, (0, 0, 255), 10)
        image = cv2.resize(masked, (800, 600))
        cv2.imshow("image", image)
        cv2.waitKey(0)
