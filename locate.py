from components.cameras import CalibratedCamera
from components.communication import Publisher
from components.localization import ColorMaskLocater

def main():
    publisher = Publisher("in_view", "5556")
    camera = CalibratedCamera("/dev/video0")
    locator = ColorMaskLocater(camera)
    for points in locator.locate(True):
        publisher.send(points)

if __name__ == "__main__":
    main()
