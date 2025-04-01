import time
from ARH.Navigation.battery_manager import BatteryManager
from ARH.Navigation.sensor_handler import SensorHandler
from ARH.Navigation.slam import RoverSLAM

class RoverNavigation:
    def __init__(self, session_id, rover_id):
        """
        Initialize the RoverNavigation class with session ID and rover ID.
        It also initializes the required battery, sensor management systems, and SLAM.
        """
        self.session_id = session_id
        self.rover_id = rover_id
        self.battery_manager = BatteryManager()  # Handles battery level and communication
        self.sensor_handler = SensorHandler(session_id, rover_id)  # Handles sensor data for survivor detection
        self.slam_system = RoverSLAM()  # Initialize SLAM system for mapping and localization

    def check_battery_and_communication(self):
        """
        Checks if the rover's battery and communication status are within operational limits.
        """
        if self.battery_manager.battery_level < 10:
            print("Battery below 10%, communication lost. Recharging needed.")
            return False

        if self.battery_manager.communication_status == "Inactive":
            print("Communication lost, waiting for recovery.")
            return False
        
        return True

    def detect_and_avoid_obstacle(self):
        """
        Use sensor data to detect obstacles and avoid them.
        """
        ultrasonic_data = self.get_sensor_data("ultrasonic")
        ir_data = self.get_sensor_data("IR")

        if self.sensor_handler.detect_obstacle(ultrasonic_data, ir_data):
            print("Obstacle detected! Avoiding it.")
            # Implement a strategy for avoiding the obstacle, e.g., stop and turn
            return True

        return False

    def move_forward(self):
        """
        Move the rover forward if no survivor is detected and battery is sufficient.
        It also considers obstacle detection before moving.
        """
        if not self.check_battery_and_communication():
            return {"message": "Cannot move forward: Battery/Communication issue."}

        if self.sensor_handler.detect_survivor():
            print("Survivor detected! Stopping rover.")
            return {"message": "Survivor detected. Stopping rover."}

        if self.detect_and_avoid_obstacle():
            print("Obstacle detected during movement! Stopping rover.")
            return {"message": "Obstacle detected. Stopping rover."}

        print("Moving forward...")
        return {"message": "Rover started moving forward"}

    def move_backward(self):
        # Similar to move_forward, with obstacle detection integrated
        pass

    def stop_rover(self):
        print("Stopping rover...")
        return {"message": "Rover stopped."}
