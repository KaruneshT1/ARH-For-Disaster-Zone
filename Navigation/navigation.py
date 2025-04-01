import time
from ARH.Navigation.battery_manager import BatteryManager
from ARH.Navigation.sensor_handler import SensorHandler
from ARH.Navigation.slam import RoverSLAM  # Assuming SLAM module is available for position updates

class RoverNavigation:
    def __init__(self, session_id, rover_id):
        """
        Initialize the RoverNavigation class with session ID and rover ID.
        Initializes the required battery, sensor management systems, and SLAM for localization and mapping.
        """
        self.session_id = session_id
        self.rover_id = rover_id
        self.battery_manager = BatteryManager()  # Handles battery level and communication
        self.sensor_handler = SensorHandler(session_id, rover_id)  # Handles sensor data for survivor detection
        self.slam_system = RoverSLAM()  # Initialize SLAM system for mapping and localization

    def check_battery_and_communication(self):
        """
        Checks if the rover's battery and communication status are within operational limits.
        Returns True if both are acceptable, otherwise returns False.
        """
        if self.battery_manager.battery_level < 10:
            return self._handle_error("Battery below 10%, communication lost. Recharging needed.")
        
        if self.battery_manager.communication_status == "Inactive":
            return self._handle_error("Communication lost, waiting for recovery.")
        
        return True

    def _handle_error(self, message):
        """
        Helper function to log and return error messages for battery or communication issues.
        """
        print(message)
        return False

    def detect_and_stop_if_survivor(self):
        """
        Detects a survivor using sensor handler, and stops the rover if found.
        Returns True if a survivor was detected, otherwise returns False.
        """
        if self.sensor_handler.detect_survivor():
            print("Survivor detected! Stopping rover.")
            return True
        return False

    def detect_and_avoid_obstacle(self):
        """
        Detect obstacles using sensors (ultrasonic, IR) and take action to avoid them.
        Returns True if an obstacle is detected and action was taken.
        """
        ultrasonic_data = self.sensor_handler.get_sensor_data("ultrasonic")
        ir_data = self.sensor_handler.get_sensor_data("IR")
        
        if self.sensor_handler.detect_obstacle(ultrasonic_data, ir_data):
            print("Obstacle detected! Taking action to avoid it.")
            # Implement obstacle avoidance strategy, e.g., stop and turn
            return True
        
        return False

    def move(self, direction):
        """
        General method to move the rover in a specified direction.
        Directions: 'forward', 'backward', 'left', 'right'.
        Returns a message dict with status.
        """
        if not self.check_battery_and_communication():
            return {"message": f"Cannot move {direction}: Battery/Communication issue."}
        
        if self.detect_and_stop_if_survivor():
            return {"message": "Survivor detected. Stopping rover."}
        
        if self.detect_and_avoid_obstacle():
            return {"message": "Obstacle detected. Stopping rover."}
        
        # Proceed with movement
        print(f"Moving {direction}...")
        self.slam_system.update_position()  # Optionally update position using SLAM
        return {"message": f"Rover started moving {direction}"}

    def return_to_base(self):
        """
        In case of emergency or recharging, return the rover to its base location.
        This would be based on internal logic to make the rover return to its starting point.
        """
        if not self.check_battery_and_communication():
            return {"message": "Cannot return to base: Battery/Communication issue."}

        print("Returning to base...")
        time.sleep(2)  # Simulate movement duration
        self.slam_system.stop_mapping()  # Optionally stop SLAM mapping
        return {"message": "Rover returning to base."}

    def stop_rover(self):
        """
        Stop the rover's movement.
        """
        print("Stopping rover...")
        self.slam_system.stop_mapping()  # Optionally stop SLAM mapping
        return {"message": "Rover stopped."}
