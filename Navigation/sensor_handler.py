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

    def detect_survivor(self, ultrasonic_data=None, ir_data=None, rfid_data=None, accelerometer_data=None):
        """
        Simulate the process of detecting survivors using sensor data.
        """
        if ultrasonic_data and ultrasonic_data.get('distance', 0) < 2.0:
            self.survivor_detected = True
            return True
        if ir_data and ir_data.get('proximity', 0) > 0.5:
            self.survivor_detected = True
            return True
        if rfid_data and rfid_data.get('tag_id', '') == 'survivor_tag':
            self.survivor_detected = True
            return True
        if accelerometer_data and any(abs(accel) > 1.0 for accel in accelerometer_data.values()):
            self.survivor_detected = True
            return True
        self.survivor_detected = False
        return False

    def detect_obstacle(self, ultrasonic_data=None, ir_data=None):
        """
        Detect obstacles using ultrasonic and IR sensor data.
        If any sensor detects an obstacle, set obstacle_detected to True.
        """
        if ultrasonic_data and ultrasonic_data.get('distance', 0) < 1.0:  # Obstacle within 1 meter
            self.obstacle_detected = True
            return True

        if ir_data and ir_data.get('proximity', 0) > 0.8:  # Proximity threshold for detecting obstacle
            self.obstacle_detected = True
            return True

        self.obstacle_detected = False
        return False

    def _check_ultrasonic(self, data):
        if not isinstance(data, dict):
            raise ValueError("Expected a dictionary for ultrasonic data.")
        return data.get('distance', 0) < 2.0

    def _check_ir(self, data):
        if not isinstance(data, dict):
            raise ValueError("Expected a dictionary for IR data.")
        return data.get('proximity', 0) > 0.5

    def _check_rfid(self, data):
        if not isinstance(data, dict):
            raise ValueError("Expected a dictionary for RFID data.")
        return data.get('tag_id', '') == 'survivor_tag'

    def _check_accelerometer(self, data):
        if not isinstance(data, dict):
            raise ValueError("Expected a dictionary for accelerometer data.")
        return any(abs(accel) > 1.0 for accel in data.values())


    def get_survivor_status(self):
        """
        Returns the current status of survivor detection.
        """
        return {"survivor_detected": self.survivor_detected}