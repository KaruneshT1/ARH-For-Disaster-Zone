import requests

class SensorHandler:
    def __init__(self, session_id, rover_id):
        self.session_id = session_id
        self.rover_id = rover_id
        self.base_url = 'https://roverdata2-production.up.railway.app/api/rover'

    def get_sensor_data(self):
        """Fetch sensor data from the rover"""
        url = f"{self.base_url}/{self.rover_id}/sensor-data?session_id={self.session_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch sensor data.")
            return None
    
    def process_ultrasonic_data(self, data):
        """Process ultrasonic data to detect obstacles or survivors"""
        if data['ultrasonic_distance'] < 2:  # Assuming < 2 meters indicates an obstacle/survivor
            return True  # Survivor detected
        return False
    
    def process_ir_data(self, data):
        """Process IR data to detect survivors or obstacles"""
        if data['ir_signal_strength'] > 0.8:  # Assuming a high IR signal strength indicates a survivor
            return True  # Survivor detected
        return False
    
    def process_rfid_data(self, data):
        """Process RFID data to detect survivors"""
        if data['rfid_tag_found']:  # If an RFID tag is detected
            return True  # Survivor detected
        return False
    
    def process_accelerometer_data(self, data):
        """Process accelerometer data to detect movement indicating a survivor"""
        if data['accelerometer_movement'] > 1.0:  # Movement threshold indicating possible survivor
            return True  # Survivor detected
        return False

    def detect_survivor(self):
        """Detect a survivor using all available sensor data"""
        sensor_data = self.get_sensor_data()
        if sensor_data:
            # Assume sensor data is returned as a dictionary containing all sensor values
            if (self.process_ultrasonic_data(sensor_data) or 
                self.process_ir_data(sensor_data) or 
                self.process_rfid_data(sensor_data) or 
                self.process_accelerometer_data(sensor_data)):
                return True  # Survivor detected
        return False
