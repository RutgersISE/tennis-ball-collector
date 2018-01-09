from components.communication import Subscriber
from components.commanders import DummyCommander
from components.trajectories import PointAndShootTrajector

def main():
    target_subscriber = Subscriber("target_rel", "5557")
    commander = DummyCommander()
    trajector = PointAndShootTrajector()
    while True:
        disp_x, disp_y = target_subscriber.listen()
        left_speed, right_speed, move_time = trajector.traject(disp_x, disp_y)
        commander.command(left_speed, right_speed, move_time)

if __name__ == "__main__":
    main()
