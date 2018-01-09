from components.communication import Publisher, Subscriber
from components.planners import NearestPointPlanner

def main():
    in_view_subscriber = Subscriber("in_view", "5556")
    target_publisher = Publisher("target_rel", "5557")
    planner = NearestPointPlanner()
    while True:
        points = in_view_subscriber.listen()
        target = planner.plan(points)
        target_publisher.send(target)

if __name__ == "__main__":
    main()
