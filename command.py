from components.communication import Subscriber, Publisher
from components.commanders import ArduinoCommander
from components.trajectories import PointAndShootTrajector

def main():
    target_subscriber = Subscriber("target_rel", "5557")
    position_publisher = Publisher("position_rel", "5558")
    commander = ArduinoCommander("/dev/ttyACM1", 38400)
    trajector = PointAndShootTrajector()
    while True:
        disp_x, disp_y = target_subscriber.listen()
        if disp_x == 0 and disp_y == 0:
            commander.command(0, 0)
            continue
        l_speed, r_speed, move_time, disp_rho, disp_phi = trajector.traject(disp_x, disp_y)
        if move_time == 0:
            commander.command(0, 0)
            continue
        print("wheel_velocity: ", (l_speed, r_speed))
        commander.command(l_speed, r_speed, move_time)
        print("position_rel: ", (disp_rho, disp_phi))
        position_publisher.send((disp_rho, disp_phi))

if __name__ == "__main__":
    main()
