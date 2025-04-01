import time
import logging
from ARH.Navigation.battery_manager import BatteryManager, BatteryError, CommunicationError
from ARH.Navigation.sensor_handler import SensorHandler
from ARH.Navigation.slam import RoverSLAM  # Assuming SLAM module is available for position updates

# Set up logging
logging.basicConfig(filename='navigation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RoverNavigation:
    def __init__(self, session_id, rover_id):
        """
        Initialize the RoverNavigation class with session ID and rover ID.
        Initializes the required battery, sensor management systems, and SLAM for localization and mapping.
        """
        self.session_id = session_id
        self.rover_id = rover_id
        
        try:
            self.battery_manager = BatteryManager()  # Handles battery level and communication
            self.sensor_handler = SensorHandler(session_id, rover_id)  # Handles sensor data for survivor detection
            self.slam_system = RoverSLAM()  # SLAM system for mapping and localization
            logging.info("RoverNavigation initialized successfully.")
        except Exception as e:
            logging.critical(f"Failed to initialize RoverNavigation: {str(e)}")
            raise RuntimeError("Critical failure in initializing rover subsystems.")

    def check_battery_and_communication(self):
        """
        Checks if the rover's battery and communication status are within operational limits.
        Returns True if both are acceptable, otherwise raises appropriate errors.
        """
        try:
            if self.battery_manager.battery_level < 10:
                raise BatteryError("Battery below 10%, communication lost. Recharging needed.")
            
            if self.battery_manager.communication_status == "Inactive":
                raise CommunicationError("Communication lost, waiting for recovery.")
            
            return True
        
        except (BatteryError, CommunicationError) as e:
            logging.warning(f"Battery/Communication issue: {str(e)}")
            return False

    def detect_and_stop_if_survivor(self):
        """
        Detects a survivor using sensor handler, and stops the rover if found.
        Returns True if a survivor was detected, otherwise returns False.
        """
        try:
            if self.sensor_handler.detect_survivor():
                logging.info("Survivor detected! Stopping rover.")
                return True
            return False
        except Exception as e:
            logging.error(f"Error detecting survivor: {str(e)}")
            return False  # Assume no survivor detected if error occurs

    def detect_and_avoid_obstacle(self):
        """
        Detect obstacles using sensors (ultrasonic, IR) and take action to avoid them.
        Returns True if an obstacle is detected and action was taken.
        """
        try:
            ultrasonic_data = self.sensor_handler.get_sensor_data("ultrasonic")
            ir_data = self.sensor_handler.get_sensor_data("IR")
            
            if self.sensor_handler.detect_obstacle(ultrasonic_data, ir_data):
                logging.info("Obstacle detected! Taking action to avoid it.")
                # Implement obstacle avoidance strategy, e.g., stop and turn
                return True
            return False
        except Exception as e:
            logging.error(f"Error detecting obstacle: {str(e)}")
            return False  # Assume no obstacle detected if error occurs

    def move(self, direction):
        """
        General method to move the rover in a specified direction.
        Directions: 'forward', 'backward', 'left', 'right'.
        Returns a message dict with status.
        """
        try:
            if not self.check_battery_and_communication():
                return {"message": f"Cannot move {direction}: Battery/Communication issue."}
            
            if self.detect_and_stop_if_survivor():
                return {"message": "Survivor detected. Stopping rover."}
            
            if self.detect_and_avoid_obstacle():
                return {"message": "Obstacle detected. Stopping rover."}
            
            # Proceed with movement
            logging.info(f"Rover moving {direction}...")
            self.slam_system.update_position()  # Update position using SLAM
            return {"message": f"Rover started moving {direction}"}
        
        except Exception as e:
            logging.error(f"Movement error: {str(e)}")
            return {"message": f"Failed to move {direction} due to an error."}

    def return_to_base(self):
        """
        In case of emergency or recharging, return the rover to its base location.
        This would be based on internal logic to make the rover return to its starting point.
        """
        try:
            if not self.check_battery_and_communication():
                return {"message": "Cannot return to base: Battery/Communication issue."}

            logging.info("Returning to base...")
            time.sleep(2)  # Simulate movement duration
            self.slam_system.stop_mapping()  # Stop SLAM mapping
            return {"message": "Rover returning to base."}
        
        except Exception as e:
            logging.error(f"Error returning to base: {str(e)}")
            return {"message": "Failed to return to base due to an error."}

    def stop_rover(self):
        """
        Stop the rover's movement.
        """
        try:
            logging.info("Stopping rover...")
            self.slam_system.stop_mapping()  # Stop SLAM mapping
            return {"message": "Rover stopped."}
        
        except Exception as e:
            logging.error(f"Error stopping rover: {str(e)}")
            return {"message": "Failed to stop rover due to an error."}
