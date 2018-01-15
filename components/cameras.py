#!/usr/bin/env python3
"""
Vision system for tennis ball collector.
"""

__author__ = "Andrew Benton"
__version__ = "0.1.0"

import numpy as np
import cv2
import os
import time
try:
    import picamera
    import picamera.array
except ImportError:
    pass

CURRDIR = os.path.dirname(__file__)
LOG_CALIBRATION_FILE = os.path.join(CURRDIR, "runtime/logitech_480p_calibration.npz")
PI_CALIBRATION_FILE = os.path.join(CURRDIR, "runtime/raspicam_v2_m4_calibration.npz")
LOG_PROJECTION_FILE = os.path.join(CURRDIR, "runtime/logitech_480p_backprojection.npz")
PI_PROJECTION_FILE = os.path.join(CURRDIR, "runtime/raspicam_v2_m4_backprojection.npz")

class CalibratedCamera(object):

    def __init__(self, device, calibration_file=LOG_CALIBRATION_FILE, fps=60, n_frames=5):
        self.device = device
        self.n_frames = n_frames
        self.calibration = np.load(calibration_file)
        self.height = self.calibration["height"]
        self.width = self.calibration["width"]
        self.map_x, self.map_y = cv2.initUndistortRectifyMap(
                                                    self.calibration["camera_matrix"],
                                                    self.calibration["dist_coeffs"],
                                                    None,
                                                    self.calibration["new_camera_matrix"],
                                                    (self.width, self.height),
                                                    5)
        self.camera = cv2.VideoCapture(device)
        if not self.camera.isOpened():
            raise RuntimeError("Camera device %s not found." % device)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camera.set(cv2.CAP_PROP_FPS, fps)

    def capture_single(self):
        average = np.zeros((self.height, self.width, 3), dtype=np.float32)
        for i in range(self.n_frames):
            ret, frame = self.camera.read()
            cv2.accumulate(frame, average)
        average = (average/float(self.n_frames)).astype(np.uint8)
        image = cv2.remap(average, self.map_x, self.map_y, cv2.INTER_LINEAR)
        return image

    def capture(self):
        while True:
            try:
                yield self.capture_single()
            except (KeyboardInterrupt, SystemExit):
                return

    def __del__(self):
        self.camera.release()

class CalibratedPicamera(object):

    def __init__(self, device=None, calibration_file=PI_CALIBRATION_FILE, fps=20, n_frames=2):
        self.n_frames = n_frames
        self.calibration = np.load(calibration_file)
        self.height = self.calibration["height"]
        self.width = self.calibration["width"]
        self.map_x, self.map_y = cv2.initUndistortRectifyMap(
                                                    self.calibration["camera_matrix"],
                                                    self.calibration["dist_coeffs"],
                                                    None,
                                                    self.calibration["new_camera_matrix"],
                                                    (self.width, self.height),
                                                    5)
        self.camera = picamera.PiCamera(sensor_mode=4, framerate=5)
        self.camera.resolution = (640, 480)
        time.sleep(2)

    def capture(self):
        with picamera.array.PiRGBArray(self.camera, size=self.camera.resolution) as stream:
            for frame in self.camera.capture_continuous(stream, format="bgr", use_video_port=True):
                try:
                    image = stream.array
                    image = cv2.remap(image, self.map_x, self.map_y, cv2.INTER_LINEAR)
                    yield image
                    stream.truncate(0)
                except (KeyboardInterrupt, SystemExit):
                    return

    def capture_single(self):
        raise NotImplementedError()

    def __del__(self):
        self.camera.close()
