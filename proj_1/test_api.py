import requests
import time
import json

API_BASE = "https://roverdata2-production.up.railway.app"

def test_api_connectivity():
    print("TESTING AUTONOMOUS RESCUE ROVER API CONNECTIVITY")
    print("-" * 50)
    
    # Step 1: Start a session
    print("\n1. Starting a new session...")
    session_id = start_session()
    if not session_id:
        print("❌ Failed to start session. API may be down.")
        return
    print(f"✅ Session started successfully! Session ID: {session_id}")
    
    # Step 2: Get rover status
    print("\n2. Getting rover status...")
    rover_status = get_rover_status(session_id)
    if "detail" in rover_status and rover_status["detail"] == "Not Found":
        print("❌ Rover status endpoint not found or incorrect.")
    else:
        print(f"✅ Rover status retrieved: {json.dumps(rover_status, indent=2)}")
    
    # Step 3: Get sensor data
    print("\n3. Getting sensor data...")
    sensor_data = get_sensor_data(session_id)
    if "detail" in sensor_data and sensor_data["detail"] == "Not Found":
        print("❌ Sensor data endpoint not found or incorrect.")
    else:
        print(f"✅ Sensor data retrieved: {json.dumps(sensor_data, indent=2)}")
    
    # Step 4: Test rover movement
    print("\n4. Testing rover movement (forward)...")
    move_result = move_rover(session_id, "forward")
    if "detail" in move_result and move_result["detail"] == "Not Found":
        print("❌ Move rover endpoint not found or incorrect.")
    else:
        print(f"✅ Move command sent: {json.dumps(move_result, indent=2)}")
    
    # Step 5: Test stopping the rover
    print("\n5. Testing rover stop command...")
    stop_result = stop_rover(session_id)
    if "detail" in stop_result and stop_result["detail"] == "Not Found":
        print("❌ Stop rover endpoint not found or incorrect.")
    else:
        print(f"✅ Stop command sent: {json.dumps(stop_result, indent=2)}")
    
    print("\nAPI TESTING COMPLETE")

def start_session():
    """Start a new session with the API"""
    try:
        response = requests.post(f"{API_BASE}/api/session/start")
        data = response.json()
        return data.get("session_id")
    except Exception as e:
        print(f"Error starting session: {e}")
        return None

def get_rover_status(session_id):
    """Get status of the rover"""
    try:
        response = requests.get(f"{API_BASE}/api/rover/Rover-1/status?session_id={session_id}")
        return response.json()
    except Exception as e:
        print(f"Error getting rover status: {e}")
        return {"error": str(e)}

def get_sensor_data(session_id):
    """Get sensor data from the rover"""
    try:
        response = requests.get(f"{API_BASE}/api/rover/Rover-1/sensor-data?session_id={session_id}")
        return response.json()
    except Exception as e:
        print(f"Error getting sensor data: {e}")
        return {"error": str(e)}

def move_rover(session_id, direction):
    """Move the rover in a specified direction"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rover/Rover-1/move?session_id={session_id}&direction={direction}"
        )
        return response.json()
    except Exception as e:
        print(f"Error moving rover: {e}")
        return {"error": str(e)}

def stop_rover(session_id):
    """Stop the rover's movement"""
    try:
        response = requests.post(f"{API_BASE}/api/rover/Rover-1/stop?session_id={session_id}")
        return response.json()
    except Exception as e:
        print(f"Error stopping rover: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    test_api_connectivity()
