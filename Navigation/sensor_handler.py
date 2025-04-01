import logging

# Set up logging
logging.basicConfig(filename='sensor_handler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SensorError(Exception):
    """Custom exception for sensor failures."""
    pass

class SensorHandler:
    def __init__(self, session_id, rover_id):
        """
        Initialize the SensorHandler with rover-specific details.
        Assumes that sensor data comes from other modules.
        """
        self.session_id = session_id
        self.rover_id = rover_id
        self.survivor_detected = False  # No survivors initially
        self.obstacle_detected = False  # No obstacles initially
        logging.info(f"SensorHandler initialized for Rover {rover_id} in session {session_id}")

    def detect_survivor(self, ultrasonic_data=None, ir_data=None, rfid_data=None, accelerometer_data=None):
        """
        Detect survivors using multiple sensor data sources.
        Returns True if a survivor is detected, otherwise False.
        """
        try:
            if self._check_ultrasonic(ultrasonic_data) or self._check_ir(ir_data) or self._check_rfid(rfid_data) or self._check_accelerometer(accelerometer_data):
                self.survivor_detected = True
                logging.info("Survivor detected!")
                return True
            
            self.survivor_detected = False
            return False

        except SensorError as e:
            logging.error(f"Sensor failure while detecting survivor: {str(e)}")
            return False  # Assume no detection if there's an error

    def detect_obstacle(self, ultrasonic_data=None, ir_data=None):
        """
        Detect obstacles using ultrasonic and IR sensor data.
        Returns True if an obstacle is detected, otherwise False.
        """
        try:
            if self._check_ultrasonic(ultrasonic_data, obstacle=True) or self._check_ir(ir_data, obstacle=True):
                self.obstacle_detected = True
                logging.info("Obstacle detected!")
                return True

            self.obstacle_detected = False
            return False

        except SensorError as e:
            logging.error(f"Sensor failure while detecting obstacle: {str(e)}")
            return False  # Assume no detection if there's an error

    def _check_ultrasonic(self, data, obstacle=False):
        """
        Check ultrasonic sensor data for survivors or obstacles.
        """
        if not isinstance(data, dict):
            raise SensorError("Invalid ultrasonic data format.")
        
        if obstacle:
            return data.get('distance', float('inf')) < 1.0  # Obstacle within 1 meter
        return data.get('distance', float('inf')) < 2.0  # Survivor within 2 meters

    def _check_ir(self, data, obstacle=False):
        """
        Check IR sensor data for survivors or obstacles.
        """
        if not isinstance(data, dict):
            raise SensorError("Invalid IR data format.")

        if obstacle:
            return data.get('proximity', 0) > 0.8  # Obstacle detection
        return data.get('proximity', 0) > 0.5  # Survivor detection

    def _check_rfid(self, data):
        """
        Check RFID sensor data for survivors.
        """
        if not isinstance(data, dict):
            raise SensorError("Invalid RFID data format.")
        
        return data.get('tag_id', '') == 'survivor_tag'

    def _check_accelerometer(self, data):
        """
        Check accelerometer data for unusual movement patterns indicating survivors.
        """
        if not isinstance(data, dict):
            raise SensorError("Invalid accelerometer data format.")
        
        return any(abs(accel) > 1.0 for accel in data.values())

    def get_survivor_status(self):
        """
        Returns the current status of survivor detection.
        """
        return {"survivor_detected": self.survivor_detected}
