from components.cameras import CalibratedPicamera
from components.communication import Publisher
from components.localization import ColorMaskLocater

def main():
    publisher = Publisher("in_view", "5556")
    camera = CalibratedPicamera()
    locator = ColorMaskLocater(camera)
    for points in locator.locate(True):
        print(points)
        publisher.send(points)

if __name__ == "__main__":
    main()
