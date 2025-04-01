import requests

# Base URL for the API
BASE_URL = "https://roverdata2-production.up.railway.app/api"

# Start a session
def start_session():
    url = f"{BASE_URL}/session/start"
    response = requests.post(url)
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data['session_id']
        print(f"Session started with ID: {session_id}")
        return session_id
    else:
        print("Error starting session")
        return None

# Get fleet status
def get_fleet_status(session_id):
    url = f"{BASE_URL}/fleet/status?session_id={session_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching fleet status")
        return None

# Get rover status
def get_rover_status(session_id):
    url = f"{BASE_URL}/rover/Rover1/status?session_id={session_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching rover status")
        return None

# Get sensor data
def get_sensor_data(session_id):
    url = f"{BASE_URL}/rover/Rover1/sensor-data?session_id={session_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching sensor data")
        return None

# Move rover
def move_rover(session_id, direction):
    url = f"{BASE_URL}/rover/Rover1/move?session_id={session_id}&direction={direction}"
    response = requests.post(url)
    if response.status_code == 200:
        print(f"Rover moved {direction}")
    else:
        print(f"Error moving rover in {direction} direction")

# Stop rover
def stop_rover(session_id):
    url = f"{BASE_URL}/rover/Rover1/stop?session_id={session_id}"
    response = requests.post(url)
    if response.status_code == 200:
        print("Rover stopped")
    else:
        print("Error stopping rover")
