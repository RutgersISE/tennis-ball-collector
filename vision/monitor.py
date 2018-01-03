import numpy as np
import cv2
import time

from localization import ColorMaskDetector, RANSACBackProjector

def watch(device, calibration_file, show=False):
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
    camera.set(cv2.CAP_PROP_FPS, 10) # high frame rate is not necessary here
    detector = ColorMaskDetector()
    backprojector = RANSACBackProjector()
    while True:
        try:
            average = np.zeros((height, width, 3), dtype=np.float32)
            for i in range(1):
                ret, frame = camera.read()
                cv2.accumulate(frame, average)
            average = (average/1.0).astype(np.uint8)
            image = cv2.remap(average, map_x, map_y, cv2.INTER_LINEAR)
            image_points, mask = detector.detect(image)
            if not image_points.size:
                continue
            object_points = backprojector.back_project(image_points, 0)
            yield object_points
            if show:
                for (img_x, img_y), (obj_x, obj_y) in zip(image_points, object_points):
                    cv2.circle(average, (img_x, img_y), 3, (0, 0, 0), -1)
                    text = "(%3.1f, %3.1f)" % (obj_x, obj_y)
                    cv2.putText(average, text, (img_x + 5, img_y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0))
                cv2.imshow("%s: analysis feed" % device, average)
                cv2.imshow("%s: color mask" % device, mask)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except (KeyboardInterrupt, SystemExit):
            break
    camera.release()

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

    for object_points in watch(args.device, args.calibration_file, True):
        print(object_points)
