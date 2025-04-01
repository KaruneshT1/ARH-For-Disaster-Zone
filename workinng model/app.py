from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

# Store session ID and rover state in memory
rover_state = {
    "session_id": None,
    "status": None,
    "battery": None,
    "communication_status": None
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
        response = requests.get(f"{API_BASE_URL}/rover/sensor-data?session_id={rover_state['session_id']}")
        if response.status_code == 200:
            sensor_data = response.json()
            
            # Update communication status in rover_state
            if 'communication_status' in sensor_data:
                rover_state['communication_status'] = sensor_data['communication_status']
            
            # Process and validate position data
            if 'position' in sensor_data and isinstance(sensor_data['position'], dict):
                # Ensure position has x, y, z coordinates
                if 'z' not in sensor_data['position']:
                    sensor_data['position']['z'] = 0  # Default if missing
            
            # Process ultrasonic data
            if 'ultrasonic' in sensor_data:
                # If ultrasonic is just a number, convert to proper format
                if isinstance(sensor_data['ultrasonic'], (int, float)):
                    distance = sensor_data['ultrasonic']
                    sensor_data['ultrasonic'] = {
                        'distance': distance,
                        'detection': distance < 100  # Example threshold, adjust as needed
                    }
            
            # Process IR data if needed
            if 'ir' in sensor_data and not isinstance(sensor_data['ir'], bool):
                # Convert to boolean if it's not already
                sensor_data['ir'] = bool(sensor_data['ir'])
            
            # Process RFID data
            if 'rfid' in sensor_data:
                # If rfid is just a string or boolean, convert to proper format
                if not isinstance(sensor_data['rfid'], dict):
                    tag_detected = bool(sensor_data['rfid'])
                    tag_id = sensor_data['rfid'] if isinstance(sensor_data['rfid'], str) else None
                    sensor_data['rfid'] = {
                        'tag_detected': tag_detected,
                        'tag_id': tag_id
                    }
            
            return jsonify(sensor_data)
    return jsonify({"error": "No active session"}), 400

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
