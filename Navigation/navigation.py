import time
from ARH.Navigation.battery_manager import BatteryManager
from ARH.Navigation.sensor_handler import SensorHandler
from ARH.Navigation.api_comm import APIComm

class RoverNavigation:
    def __init__(self, session_id, rover_id):
        """
        Initialize the RoverNavigation class with session ID and rover ID.
        It also initializes the required communication, battery, and sensor management systems.
        """
        self.session_id = session_id
        self.rover_id = rover_id
        self.api = APIComm(session_id, rover_id)
        self.battery_manager = BatteryManager()  # Initializing battery manager to handle battery status
        self.sensor_handler = SensorHandler(session_id, rover_id)  # Initializing sensor handler to detect survivors

    def check_battery_and_communication(self):
        """
        Check if the rover's battery and communication status are within operational limits.
        Returns True if both are within acceptable limits, otherwise False.
        """
        # Checking battery level is sufficient for operation
        if self.battery_manager.battery_level < self.battery_manager.low_battery_threshold:
            print("Battery below threshold, communication lost. Recharging needed.")
            return False

        # Checking if communication is active
        if not self.api.is_communication_active():
            print("Communication lost, waiting for recovery.")
            return False

        return True

    def move_forward(self):
        """
        Move the rover forward if no survivor is detected and battery is sufficient.
        """
        if not self.check_battery_and_communication():
            return {"message": "Cannot move forward: Battery/Communication issue."}
        
        if self.sensor_handler.detect_survivor():
            print("Survivor detected! Stopping rover.")
            self.api.stop_rover()
            return {"message": "Survivor detected. Stopping rover."}
        
        print("Moving forward...")
        self.api.move_rover("forward")
        return {"message": "Rover started moving forward"}

    def move_backward(self):
        """
        Move the rover backward if no survivor is detected and battery is sufficient.
        """
        if not self.check_battery_and_communication():
            return {"message": "Cannot move backward: Battery/Communication issue."}

        if self.sensor_handler.detect_survivor():
            print("Survivor detected! Stopping rover.")
            self.api.stop_rover()
            return {"message": "Survivor detected. Stopping rover."}
        
        print("Moving backward...")
        self.api.move_rover("backward")
        return {"message": "Rover started moving backward"}

    def move_left(self):
        """
        Move the rover left if no survivor is detected and battery is sufficient.
        """
        if not self.check_battery_and_communication():
            return {"message": "Cannot move left: Battery/Communication issue."}

        if self.sensor_handler.detect_survivor():
            print("Survivor detected! Stopping rover.")
            self.api.stop_rover()
            return {"message": "Survivor detected. Stopping rover."}

        print("Moving left...")
        self.api.move_rover("left")
        return {"message": "Rover started moving left"}

    def move_right(self):
        """
        Move the rover right if no survivor is detected and battery is sufficient.
        """
        if not self.check_battery_and_communication():
            return {"message": "Cannot move right: Battery/Communication issue."}

        if self.sensor_handler.detect_survivor():
            print("Survivor detected! Stopping rover.")
            self.api.stop_rover()
            return {"message": "Survivor detected. Stopping rover."}

        print("Moving right...")
        self.api.move_rover("right")
        return {"message": "Rover started moving right"}

    def return_to_base(self):
        """
        In case of emergency or recharging, return the rover to its base location.
        This would be based on internal logic to make the rover return to its starting point.
        """
        if not self.check_battery_and_communication():
            return {"message": "Cannot return to base: Battery/Communication issue."}

        print("Returning to base...")
        self.api.move_rover("backward")
        time.sleep(2)  # Simulate movement duration for the rover to return
        return {"message": "Rover returning to base."}

    def stop_rover(self):
        """
        Stop the rover's movement if required.
        """
        self.api.stop_rover()
        return {"message": "Rover stopped."}

    def monitor_and_handle_battery(self):
        """
        Periodically check the battery status and take necessary actions if the battery level is critical or needs recharging.
        This can be used in other systems to automatically handle low battery situations.
        """
        self.battery_manager.handle_battery_cycle()

# Example of usage:

if __name__ == "__main__":
    # Initialize RoverNavigation with sample session and rover IDs
    rover_navigation = RoverNavigation(session_id="1234", rover_id="Rover_01")
    
    # Sample rover navigation actions based on battery and communication checks
    print(rover_navigation.move_forward())
    print(rover_navigation.move_left())
    print(rover_navigation.move_backward())
    print(rover_navigation.stop_rover())
    print(rover_navigation.return_to_base())