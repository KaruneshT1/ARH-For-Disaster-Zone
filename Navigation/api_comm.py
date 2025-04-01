import requests

class APIComm:
    def __init__(self, session_id, rover_id="Rover1"):
        self.session_id = session_id
        self.rover_id = rover_id
        self.base_url = "https://roverdata2-production.up.railway.app/api"

    @staticmethod
    def start_session():
        url = "https://roverdata2-production.up.railway.app/api/session/start"
        response = requests.post(url)
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data['session_id']
            print(f"Session started with ID: {session_id}")
            return session_id
        else:
            print("Error starting session")
            return None

    def get_fleet_status(self):
        url = f"{self.base_url}/fleet/status?session_id={self.session_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching fleet status")
            return None

    def get_rover_status(self):
        url = f"{self.base_url}/rover/{self.rover_id}/status?session_id={self.session_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching rover status")
            return None

    def get_sensor_data(self):
        url = f"{self.base_url}/rover/{self.rover_id}/sensor-data?session_id={self.session_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching sensor data")
            return None

    def move_rover(self, direction):
        url = f"{self.base_url}/rover/{self.rover_id}/move?session_id={self.session_id}&direction={direction}"
        response = requests.post(url)
        if response.status_code == 200:
            print(f"Rover moved {direction}")
        else:
            print(f"Error moving rover in {direction} direction")

    def stop_rover(self):
        url = f"{self.base_url}/rover/{self.rover_id}/stop?session_id={self.session_id}"
        response = requests.post(url)
        if response.status_code == 200:
            print("Rover stopped")
        else:
            print("Error stopping rover")
