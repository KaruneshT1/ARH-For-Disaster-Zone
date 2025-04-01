from flask import Flask, jsonify, render_template
import requests
import time
from datetime import datetime, timedelta

app = Flask(__name__)

# Store session ID and rover state in memory
rover_state = {
    "session_id": None,
    "status": None,
    "battery": None,
    "communication_status": None
}

# Cache for sensor data to reduce API calls
sensor_data_cache = {
    "data": None,
    "timestamp": None,
    "expiry": 2  # Cache expiry in seconds
}

API_BASE_URL = "https://roverdata2-production.up.railway.app/api"

# Serve the main rover control interface
@app.route('/')
def index():
    """Render the main rover control interface."""
    return render_template('index.html')

# Start a new session and return the session ID
@app.route('/start-session', methods=['POST'])
def start_session():
    """Start a new session and return the session ID."""
    response = requests.post(f"{API_BASE_URL}/session/start")
    if response.status_code == 200:
        session_data = response.json()
        rover_state['session_id'] = session_data.get('session_id')
        return jsonify(session_data)
    return jsonify({"error": "Failed to start session"}), 500

# Fetch rover status using the stored session ID
@app.route('/rover/status', methods=['GET'])
def get_rover_status():
    """Fetch the rover status using the stored session ID."""
    if rover_state['session_id']:
        response = requests.get(f"{API_BASE_URL}/rover/status?session_id={rover_state['session_id']}")
        if response.status_code == 200:
            rover_state['status'] = response.json()
            return jsonify(rover_state['status'])
    return jsonify({"error": "No active session"}), 400

# Fetch sensor data using the stored session ID
@app.route('/rover/sensor-data', methods=['GET'])
def get_sensor_data():
    """Fetch sensor data using the stored session ID."""
    if rover_state['session_id']:
        # Check if we have cached data that's still fresh
        current_time = time.time()
        if (sensor_data_cache["data"] is not None and 
            sensor_data_cache["timestamp"] is not None and 
            current_time - sensor_data_cache["timestamp"] < sensor_data_cache["expiry"]):
            # Return cached data if it's still fresh
            return jsonify(sensor_data_cache["data"])
        
        # Otherwise, fetch new data from API
        response = requests.get(f"{API_BASE_URL}/rover/sensor-data?session_id={rover_state['session_id']}")
        if response.status_code == 200:
            sensor_data = response.json()
            
            # Update communication status in rover_state
            if 'communication_status' in sensor_data:
                rover_state['communication_status'] = sensor_data['communication_status']
            
            # Process battery level data
            if 'battery' in sensor_data:
                rover_state['battery'] = sensor_data['battery']
                # Ensure battery_level field exists for HTML template
                sensor_data['battery_level'] = sensor_data['battery']
            
            # Process position data
            if 'position' in sensor_data:
                if not isinstance(sensor_data['position'], dict):
                    # Convert to dict if it's not already
                    if isinstance(sensor_data['position'], list) and len(sensor_data['position']) >= 2:
                        sensor_data['position'] = {
                            'x': sensor_data['position'][0],
                            'y': sensor_data['position'][1]
                        }
                    else:
                        sensor_data['position'] = {'x': 0, 'y': 0}
            else:
                sensor_data['position'] = {'x': 0, 'y': 0}
            
            # Process accelerometer data
            if 'accelerometer' in sensor_data:
                # If accelerometer is not a dict, convert it to proper format
                if not isinstance(sensor_data['accelerometer'], dict):
                    # Handle case where accelerometer might be a single value or array
                    if isinstance(sensor_data['accelerometer'], (int, float)):
                        # Single value - assume it's magnitude
                        magnitude = sensor_data['accelerometer']
                        sensor_data['accelerometer'] = {
                            'x': magnitude,
                            'y': 0,
                            'z': 0
                        }
                    elif isinstance(sensor_data['accelerometer'], list):
                        # Array format - map to x, y, z
                        accel_data = sensor_data['accelerometer']
                        sensor_data['accelerometer'] = {
                            'x': accel_data[0] if len(accel_data) > 0 else 0,
                            'y': accel_data[1] if len(accel_data) > 1 else 0,
                            'z': accel_data[2] if len(accel_data) > 2 else 0
                        }
                    else:
                        # Default empty structure
                        sensor_data['accelerometer'] = {'x': 0, 'y': 0, 'z': 0}
                else:
                    # It's already a dict, make sure it has all coordinates
                    if 'x' not in sensor_data['accelerometer']:
                        sensor_data['accelerometer']['x'] = 0
                    if 'y' not in sensor_data['accelerometer']:
                        sensor_data['accelerometer']['y'] = 0
                    if 'z' not in sensor_data['accelerometer']:
                        sensor_data['accelerometer']['z'] = 0
            else:
                sensor_data['accelerometer'] = {'x': 0, 'y': 0, 'z': 0}
            
            # Process ultrasonic data
            if 'ultrasonic' in sensor_data:
                if not isinstance(sensor_data['ultrasonic'], dict):
                    # Convert to dict with both distance and detection fields
                    if sensor_data['ultrasonic'] is None:
                        sensor_data['ultrasonic'] = {
                            'distance': None,
                            'detection': False
                        }
                    else:
                        distance = float(sensor_data['ultrasonic'])
                        sensor_data['ultrasonic'] = {
                            'distance': distance,
                            'detection': distance < 100  # Example threshold
                        }
                elif 'detection' not in sensor_data['ultrasonic'] and 'distance' in sensor_data['ultrasonic']:
                    # Add detection if only distance exists
                    distance = sensor_data['ultrasonic']['distance']
                    if distance is not None:
                        sensor_data['ultrasonic']['detection'] = distance < 100
                    else:
                        sensor_data['ultrasonic']['detection'] = False
            else:
                sensor_data['ultrasonic'] = {'distance': None, 'detection': False}
            
            # Process IR data to match HTML expected structure
            if 'ir' in sensor_data:
                ir_value = sensor_data['ir']
                # Convert to expected structure with reflection property
                if not isinstance(ir_value, dict):
                    sensor_data['ir'] = {
                        'reflection': bool(ir_value)
                    }
                elif 'reflection' not in sensor_data['ir']:
                    # If it's a dict but missing reflection field
                    sensor_data['ir']['reflection'] = bool(next(iter(sensor_data['ir'].values())))
            else:
                sensor_data['ir'] = {'reflection': False}
            
            # Process RFID data
            if 'rfid' in sensor_data:
                if not isinstance(sensor_data['rfid'], dict):
                    # Convert to expected structure
                    tag_detected = bool(sensor_data['rfid'])
                    tag_id = sensor_data['rfid'] if isinstance(sensor_data['rfid'], str) else None
                    sensor_data['rfid'] = {
                        'tag_detected': tag_detected,
                        'tag_id': tag_id
                    }
                elif 'tag_detected' not in sensor_data['rfid']:
                    # Ensure tag_detected exists
                    sensor_data['rfid']['tag_detected'] = bool(next(iter(sensor_data['rfid'].values()), False))
            else:
                sensor_data['rfid'] = {'tag_detected': False}
            
            # Add timestamp data if missing
            if 'timestamp' not in sensor_data:
                sensor_data['timestamp'] = int(time.time())
            
            # Add readable time if missing
            if 'readable_time' not in sensor_data:
                sensor_data['readable_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add recharging status if missing
            if 'recharging' not in sensor_data:
                sensor_data['recharging'] = False
            
            # Update the cache
            sensor_data_cache["data"] = sensor_data
            sensor_data_cache["timestamp"] = current_time
            
            return jsonify(sensor_data)
    return jsonify({"error": "No active session"}), 400

# Additional endpoint to force refresh sensor data (bypassing cache)
@app.route('/rover/sensor-data/refresh', methods=['GET'])
def refresh_sensor_data():
    """Force refresh of sensor data, bypassing the cache."""
    # Clear the cache
    sensor_data_cache["data"] = None
    sensor_data_cache["timestamp"] = None
    # Call the regular sensor data endpoint
    return get_sensor_data()

# Control rover movement in a specified direction
@app.route('/rover/move/<direction>', methods=['POST'])
def move_rover(direction):
    """Move the rover in a specified direction."""
    if rover_state['session_id']:
        response = requests.post(f"{API_BASE_URL}/rover/move?session_id={rover_state['session_id']}&direction={direction}")
        if response.status_code == 200:
            return jsonify({"message": f"Rover moved {direction}"})
    return jsonify({"error": "No active session"}), 400

# Recharge the rover
@app.route('/rover/recharge', methods=['POST'])
def recharge_rover():
    """Recharge the rover."""
    if rover_state['session_id']:
        response = requests.post(f"{API_BASE_URL}/rover/charge?session_id={rover_state['session_id']}")
        if response.status_code == 200:
            return jsonify({"message": "Rover is recharging"})
    return jsonify({"error": "No active session"}), 400

# Stop the rover
@app.route('/rover/stop', methods=['POST'])
def stop_rover():
    """Stop the rover."""
    if rover_state['session_id']:
        response = requests.post(f"{API_BASE_URL}/rover/stop?session_id={rover_state['session_id']}")
        if response.status_code == 200:
            return jsonify({"message": "Rover stopped"})
    return jsonify({"error": "No active session"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
