from flask import Flask, jsonify, render_template, request
import requests
import logging
import threading
import time  # Make sure time is properly imported at the top level
import json
from datetime import datetime, timedelta
from rover_direction import determine_rover_direction
from config import API_BASE_URL
import traceback

app = Flask(__name__)

# Store session ID and rover state in memory
rover_state = {
    "session_id": None,
    "status": None,
    "battery": None,
    "communication_status": None,
    "initial_position": None,  # Added to store initial position
    "final_position": None,    # Added to store final position
    "navigation_status": "Not started",  # Track navigation status
    "current_position": None,  # Track current position during navigation
    "current_direction": None,  # Track current direction during navigation
    "last_position_before_recharge": None,  # Store position before recharging
    "navigation_active": False  # Flag to track if navigation is active
}

# Cache for sensor data to reduce API calls
sensor_data_cache = {
    "data": None,
    "timestamp": None,
    "expiry": 2  # Cache expiry in seconds
}

# Navigation thread reference
navigation_thread = None

# If API_BASE_URL is not set, use the default
if not API_BASE_URL:
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
                        print(sensor_data)
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
                    # Handle case where IR might be a single value
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
@app.route('/rover/refresh-sensor-data', methods=['GET'])
def refresh_sensor_data():
    """Force refresh of sensor data, bypassing the cache."""
    # Clear the cache to force a fresh fetch
    sensor_data_cache["data"] = None
    sensor_data_cache["timestamp"] = None
    # Call the get_sensor_data function to fetch fresh data
    return get_sensor_data()

# Control rover movement in a specified direction
@app.route('/rover/move/<direction>', methods=['POST'])
def move_rover(direction):
    """Move the rover in a specified direction."""
    if rover_state['session_id']:
        response = requests.post(f"{API_BASE_URL}/rover/move?session_id={rover_state['session_id']}&direction={direction}")
        if response.status_code == 200:
            return jsonify({"success": True, "message": f"Rover moving {direction}"})
    return jsonify({"error": "Failed to move rover"}), 400

# Recharge the rover
@app.route('/rover/recharge', methods=['POST'])
def recharge_rover():
    """Recharge the rover."""
    if rover_state['session_id']:
        response = requests.post(f"{API_BASE_URL}/rover/charge?session_id={rover_state['session_id']}")
        if response.status_code == 200:
            return jsonify(response.json())
    return jsonify({"error": "Failed to recharge rover"}), 400

# Stop the rover
@app.route('/rover/stop', methods=['POST'])
def stop_rover():
    """Stop the rover."""
    if rover_state['session_id']:
        try:
            stop_url = f"{API_BASE_URL}/rover/stop?session_id={rover_state['session_id']}"
            print(f"Stopping rover with request to: {stop_url}")
            stop_response = requests.post(stop_url)
            print(f"Stop response: {stop_response.status_code}")
        except Exception as e:
            print(f"Error stopping rover: {str(e)}")
    
    rover_state['navigation_status'] = "Stopped"
    return jsonify({"success": True, "message": "Rover stopped"})

# Store initial position and start auto navigation
@app.route('/auto-navigate/start', methods=['POST'])
def start_auto_navigate():
    """Start auto-navigation by fetching current position and starting navigation thread."""
    global navigation_thread
    
    try:
        print("Start auto-navigate endpoint called")
        
        if not rover_state['session_id']:
            return jsonify({"error": "No active session. Please start a session first."}), 400
        
        # Check if navigation is already active
        if rover_state['navigation_active']:
            return jsonify({"message": "Auto-navigation is already running"}), 200
        
        # Reset navigation status
        rover_state['navigation_status'] = "Starting auto-navigation"
        rover_state['navigation_active'] = True
        
        # Get current status including position
        try:
            status_url = f"{API_BASE_URL}/rover/status?session_id={rover_state['session_id']}"
            print(f"Fetching initial rover status from: {status_url}")
            
            response = requests.get(status_url)
            print(f"Status response code: {response.status_code}")
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"Initial status data: {status_data}")
                
                if 'position' in status_data:
                    position = status_data['position']
                    if not isinstance(position, dict):
                        if isinstance(position, list) and len(position) >= 2:
                            position = {'x': position[0], 'y': position[1]}
                        else:
                            position = {'x': 0, 'y': 0}
                    
                    # Ensure position is valid before setting initial position
                    if isinstance(position, dict) and 'x' in position and 'y' in position:
                        # Set initial position if not already set
                        if not rover_state['initial_position']:
                            rover_state['initial_position'] = position
                            print(f"Initial position set: {position}")
                    else:
                        print("Invalid position data received, cannot set initial position")
                    
                    # Update current position
                    rover_state['current_position'] = position
                    print(f"Current position updated: {position}")
                else:
                    if 'coordinates' in status_data:
                        coordinates = status_data['coordinates']
                        if isinstance(coordinates, list) and len(coordinates) >= 2:
                            rover_state['initial_position'] = {'x': coordinates[0], 'y': coordinates[1]}
                            print(f"Initial position set from coordinates: {rover_state['initial_position']}")
                        else:
                            print("Invalid coordinates data received, cannot set initial position")
                    print("No position data found in status response")
            else:
                print(f"Failed to get status: {response.text}")
                return jsonify({"error": f"Failed to get rover status: {response.status_code}"}), response.status_code
                
        except Exception as e:
            print(f"Exception getting status: {str(e)}")
            traceback.print_exc()
            return jsonify({"error": f"Error getting rover status: {str(e)}"}), 500
        
        # Start auto-navigation thread
        try:
            # Stop any existing thread
            if navigation_thread and navigation_thread.is_alive():
                rover_state['navigation_active'] = False
                # Give the thread time to exit cleanly
                time.sleep(1)
            
            # Create and start new thread
            rover_state['navigation_active'] = True
            navigation_thread = threading.Thread(target=auto_navigation_thread)
            navigation_thread.daemon = True
            navigation_thread.start()
            
            return jsonify({
                "success": True,
                "message": "Auto-navigation started",
                "initial_position": rover_state['initial_position']
            })
        except Exception as e:
            print(f"Exception starting navigation thread: {str(e)}")
            traceback.print_exc()
            rover_state['navigation_active'] = False
            return jsonify({"error": f"Error starting auto-navigation: {str(e)}"}), 500
    except Exception as e:
        print(f"General exception in start_auto_navigate: {str(e)}")
        traceback.print_exc()
        rover_state['navigation_active'] = False
        return jsonify({"error": f"Error starting auto-navigation: {str(e)}"}), 500

@app.route('/auto-navigate/stop', methods=['POST'])
def stop_auto_navigate():
    """Stop auto-navigation."""
    global navigation_thread
    
    try:
        # Signal the thread to stop
        rover_state['navigation_active'] = False
        
        # Stop the rover
        if rover_state['session_id']:
            try:
                stop_url = f"{API_BASE_URL}/rover/stop?session_id={rover_state['session_id']}"
                response = requests.post(stop_url)
                print(f"Stop response: {response.status_code}")
            except Exception as e:
                print(f"Error stopping rover: {str(e)}")
        
        # Update status
        rover_state['navigation_status'] = "Stopped manually"
        
        return jsonify({
            "success": True,
            "message": "Auto-navigation stopped"
        })
    except Exception as e:
        print(f"Exception stopping auto-navigation: {str(e)}")
        return jsonify({"error": f"Error stopping auto-navigation: {str(e)}"}), 500

# Main auto-navigation thread function
def auto_navigation_thread():
    """Main thread function for auto-navigation."""
    try:
        # Initialize direction
        current_direction = "forward"
        rover_state['current_direction'] = current_direction
        
        # Main navigation loop
        while rover_state['navigation_active'] and rover_state['session_id']:
            try:
                # Run a single navigation step
                next_direction = auto_navigate(current_direction)
                
                # Check if we need to update the direction
                if next_direction:
                    current_direction = next_direction
                    rover_state['current_direction'] = current_direction
                    print(f"Direction updated to: {current_direction}")
                
                # Check for completion
                if rover_state['navigation_status'] == "Completed" or "Supply Dropped" in rover_state['navigation_status']:
                    print("Navigation completed successfully")
                    break
                
                # Check for failure
                if "Failed" in rover_state['navigation_status']:
                    print(f"Navigation failed: {rover_state['navigation_status']}")
                    break
                
                # Wait between steps
                time.sleep(3)
            except Exception as e:
                print(f"Error in navigation step: {str(e)}")
                traceback.print_exc()
                rover_state['navigation_status'] = f"Failed: {str(e)}"
                time.sleep(5)  # Wait longer after an error
        
        print("Navigation thread exiting")
    except Exception as e:
        print(f"Fatal error in navigation thread: {str(e)}")
        traceback.print_exc()
        rover_state['navigation_status'] = f"Failed: {str(e)}"
    finally:
        # Ensure navigation_active is set to False when the thread exits
        rover_state['navigation_active'] = False

# Auto-navigate function - single navigation step
def auto_navigate(current_direction):
    """Auto navigate the rover based on sensor data and direction logic. Returns the next direction."""
    try:
        if not rover_state['session_id']:
            rover_state['navigation_status'] = "Failed: No active session"
            return None
        
        print(f"Auto-navigating with session {rover_state['session_id']}, current direction: {current_direction}")
        
        # --------------------------------------------------------------
        # BATTERY CHECK AND RECHARGE - SIMPLIFIED AND MORE DIRECT
        # --------------------------------------------------------------
        need_recharge = False
        battery_level = None
        
        # Always check battery status first
        try:
            print("*** CHECKING BATTERY STATUS ***")
            status_url = f"{API_BASE_URL}/rover/status?session_id={rover_state['session_id']}"
            status_response = requests.get(status_url, timeout=15)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Status data: {status_data}")
                
                # Check battery in any form it might appear
                # First check the battery field directly
                if 'battery' in status_data:
                    bat_data = status_data['battery']
                    if isinstance(bat_data, dict) and 'level' in bat_data:
                        battery_level = bat_data['level']
                    elif isinstance(bat_data, (int, float)):
                        battery_level = bat_data
                    
                    print(f"BATTERY LEVEL: {battery_level}%")
                    
                    if battery_level is not None and battery_level <= 20:  # More aggressive threshold
                        need_recharge = True
                        print(f"*** LOW BATTERY DETECTED: {battery_level}% - RECHARGE NEEDED ***")
                
                # Also check if the status field indicates low battery
                if 'status' in status_data:
                    status_text = str(status_data['status']).lower()
                    if 'low' in status_text or 'battery' in status_text or 'intermittent' in status_text:
                        need_recharge = True
                        print(f"*** STATUS INDICATES RECHARGE NEEDED: {status_data['status']} ***")
                
                # Additional direct check for any fields that might indicate battery status
                for key, value in status_data.items():
                    if isinstance(value, str) and ('low' in value.lower() or 'battery' in value.lower()):
                        need_recharge = True
                        print(f"*** DETECTED BATTERY ISSUE IN FIELD {key}: {value} ***")
            else:
                print(f"Failed to get status: {status_response.status_code}")
                # Assume we need to recharge if we get an error
                need_recharge = True
        except Exception as e:
            print(f"Error checking battery: {str(e)}")
            # Assume we need to recharge if there's an exception
            need_recharge = True
        
        # If we need to recharge, do it immediately
        if need_recharge:
            print("==========================================================")
            print("=============== INITIATING AUTO RECHARGE =================")
            print("==========================================================")
            
            # Save current direction
            last_direction = current_direction
            
            # Stop the rover first
            try:
                print("Stopping rover before recharge...")
                stop_url = f"{API_BASE_URL}/rover/stop?session_id={rover_state['session_id']}"
                stop_response = requests.post(stop_url, timeout=10)
                print(f"Stop response: {stop_response.status_code}")
                time.sleep(2)  # Brief pause after stopping
            except Exception as e:
                print(f"Error stopping rover: {str(e)}")
            
            # Update UI
            rover_state['navigation_status'] = "LOW BATTERY - RECHARGING"
            
            # Execute recharge - very direct approach
            print("EXECUTING RECHARGE...")
            
            recharge_success = False
            for attempt in range(1, 6):  # 5 attempts
                try:
                    print(f"Recharge attempt {attempt}/5...")
                    recharge_url = f"{API_BASE_URL}/rover/charge?session_id={rover_state['session_id']}"
                    recharge_response = requests.post(recharge_url, timeout=20)
                    
                    if recharge_response.status_code == 200:
                        print(f"RECHARGE SUCCESS! Response: {recharge_response.text}")
                        recharge_success = True
                        break
                    else:
                        print(f"Recharge attempt {attempt} failed: {recharge_response.status_code}")
                except Exception as e:
                    print(f"Error during recharge attempt {attempt}: {str(e)}")
                
                # Wait between attempts
                time.sleep(3)
            
            if recharge_success:
                print("RECHARGE COMPLETED SUCCESSFULLY")
                rover_state['navigation_status'] = "Recharged - Resuming exploration"
                
                # Wait for systems to stabilize
                time.sleep(3)
                
                # Resume movement
                try:
                    print(f"Resuming movement in direction: {last_direction}")
                    move_url = f"{API_BASE_URL}/rover/move?session_id={rover_state['session_id']}&direction={last_direction.lower()}"
                    move_response = requests.post(move_url, timeout=10)
                    
                    if move_response.status_code == 200:
                        print("Movement resumed successfully")
                    else:
                        print(f"Failed to resume movement: {move_response.status_code}")
                except Exception as e:
                    print(f"Error resuming movement: {str(e)}")
            else:
                print("ALL RECHARGE ATTEMPTS FAILED")
                rover_state['navigation_status'] = "Recharge failed - attempting to continue"
            
            # Always return the last direction to maintain course
            return last_direction
        
        # Get sensor data with retry logic
        max_retries = 3
        sensor_data = None
        
        for retry in range(max_retries):
            try:
                sensor_url = f"{API_BASE_URL}/rover/sensor-data?session_id={rover_state['session_id']}"
                print(f"Requesting sensor data from: {sensor_url} (attempt {retry+1})")
                response = requests.get(sensor_url, timeout=15)
                print(f"Sensor data response code: {response.status_code}")
                
                if response.status_code == 200:
                    sensor_data = response.json()
                    print(f"Received sensor data: {sensor_data}")
                    break
                elif response.status_code == 502:
                    print(f"502 error on sensor data attempt {retry+1} - communication issues")
                    time.sleep(2 * (retry + 1))  # Exponential backoff
                else:
                    print(f"Failed to get sensor data: {response.status_code} - {response.text}")
                    time.sleep(2)
            except Exception as e:
                print(f"Exception getting sensor data (attempt {retry+1}): {str(e)}")
                time.sleep(2)
        
        if not sensor_data:
            rover_state['navigation_status'] = f"Failed: Could not get sensor data after {max_retries} attempts"
            return
        
        # CAREFULLY Extract required sensor values for direction determination AND SUPPLY DROP CHECK
        # Initialize with defaults to ensure values exist
        rfid_detected = False
        ir_detected = False
        ultrasonic_data = (0, False)
        accelerometer_data = [0, 0, 0]
        
        # Process RFID data - CRITICAL FOR SUPPLY DROP
        if 'rfid' in sensor_data:
            rfid_data = sensor_data['rfid']
            # DETAILED LOGGING for RFID data
            print(f"RFID data raw value: {rfid_data}")
            
            if isinstance(rfid_data, dict):
                if 'tag_detected' in rfid_data:
                    rfid_detected = rfid_data['tag_detected']
                elif 'detected' in rfid_data:
                    rfid_detected = rfid_data['detected']
                elif 'value' in rfid_data:
                    rfid_detected = bool(rfid_data['value'])
            elif isinstance(rfid_data, bool):
                rfid_detected = rfid_data
            elif isinstance(rfid_data, (int, float, str)):
                # Convert various data types to boolean
                if isinstance(rfid_data, str):
                    rfid_detected = rfid_data.lower() in ('true', 'yes', '1', 'detected')
                else:
                    rfid_detected = bool(rfid_data)
        
        # Explicit logging of RFID detection status
        print(f"*** RFID DETECTION STATUS: {rfid_detected} ***")
        
        # Process IR data
        if 'ir' in sensor_data:
            ir_data = sensor_data['ir']
            print(f"IR data raw value: {ir_data}")
            
            if isinstance(ir_data, dict):
                if 'reflection' in ir_data:
                    ir_detected = ir_data['reflection']
                elif 'detected' in ir_data:
                    ir_detected = ir_data['detected']
                elif 'value' in ir_data:
                    ir_detected = bool(ir_data['value'])
            elif isinstance(ir_data, bool):
                ir_detected = ir_data
            elif isinstance(ir_data, (int, float, str)):
                if isinstance(ir_data, str):
                    ir_detected = ir_data.lower() in ('true', 'yes', '1', 'detected')
                else:
                    ir_detected = bool(ir_data)
        
        print(f"IR DETECTION STATUS: {ir_detected}")
        
        # Process ultrasonic data
        if 'ultrasonic' in sensor_data:
            us_data = sensor_data['ultrasonic']
            print(f"Ultrasonic data raw value: {us_data}")
            
            distance = 0
            detection = False
            
            if isinstance(us_data, dict):
                distance = us_data.get('distance', 0)
                detection = us_data.get('detection', False)
                if 'detected' in us_data:
                    detection = us_data['detected']
            elif isinstance(us_data, (int, float)):
                distance = float(us_data) if us_data is not None else 0
                detection = distance < 100  # Example threshold
            
            ultrasonic_data = (distance, detection)
        
        print(f"ULTRASONIC DETECTION: Distance={ultrasonic_data[0]}, Detected={ultrasonic_data[1]}")
        
        # Process accelerometer data
        if 'accelerometer' in sensor_data:
            accel_data = sensor_data['accelerometer']
            if isinstance(accel_data, dict):
                accelerometer_data = [accel_data.get('x', 0), accel_data.get('y', 0), accel_data.get('z', 0)]
            elif isinstance(accel_data, list) and len(accel_data) >= 3:
                accelerometer_data = accel_data[0:3]
        
        # Process position data
        if 'position' in sensor_data:
            position = sensor_data['position']
            if isinstance(position, dict):
                rover_state['current_position'] = position
                print(f"Updated current position from sensor data: {position}")
            elif isinstance(position, list) and len(position) >= 2:
                rover_state['current_position'] = {'x': position[0], 'y': position[1]}
                print(f"Updated current position from sensor data array: {rover_state['current_position']}")
            else:
                print(f"Unexpected position format: {position}")
        else:
            print("No position data found in sensor response")
        
        # SUPPLY DROP CONDITION CHECK - SIMPLIFIED AND MORE DIRECT
        # Special case: If RFID is detected, consider this as a supply drop point
        if rfid_detected:
            print("*********************************")
            print("* RFID TAG DETECTED - SUPPLY DROP POINT REACHED *")
            print("*********************************")
            rover_state['navigation_status'] = "Supply drop point reached - RFID detected"
            
            # Get current position as the final position
            if rover_state['current_position']:
                rover_state['final_position'] = rover_state['current_position']
                print(f"Supply drop position set: {rover_state['final_position']}")
            
            # Stop the rover
            try:
                stop_url = f"{API_BASE_URL}/rover/stop?session_id={rover_state['session_id']}"
                print(f"Stopping rover with request to: {stop_url}")
                stop_response = requests.post(stop_url)
                print(f"Stop response: {stop_response.status_code}")
            except Exception as e:
                print(f"Error stopping rover: {str(e)}")
            
            rover_state['navigation_status'] = "Completed - Supply Dropped at RFID location"
            print("THE PACKAGE HAS BEEN DROPPED AT RFID LOCATION!")
            return
        
        # Determine next direction
        try:
            next_direction = determine_rover_direction(
                current_direction or "forward",  # Default to forward if no current direction
                rfid_detected, 
                ir_detected, 
                ultrasonic_data, 
                accelerometer_data
            )
            print(f"Determined direction: {next_direction}")
            rover_state['current_direction'] = next_direction
        except Exception as e:
            rover_state['navigation_status'] = f"Failed: Error determining direction: {str(e)}"
            print(f"Exception determining direction: {str(e)}")
            return
        
        # Check if we've reached the destination
        if next_direction.lower() == "reached":
            # Package is ready for dispatch - stop the rover
            rover_state['navigation_status'] = "Package ready for dispatch"
            print("Destination reached, package ready for dispatch")
            
            # Get current position before stopping
            try:
                status_response = requests.get(f"{API_BASE_URL}/rover/status?session_id={rover_state['session_id']}")
                print(f"Status response at destination: {status_response.status_code}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Final status data: {status_data}")
                    
                    if 'position' in status_data:
                        position = status_data['position']
                        if not isinstance(position, dict):
                            if isinstance(position, list) and len(position) >= 2:
                                position = {'x': position[0], 'y': position[1]}
                            else:
                                position = {'x': 0, 'y': 0}
                        rover_state['final_position'] = position
                        rover_state['current_position'] = position
                        print(f"Final position set: {position}")
            except Exception as e:
                print(f"Error getting final status: {str(e)}")
        
            # Stop the rover
            try:
                stop_url = f"{API_BASE_URL}/rover/stop?session_id={rover_state['session_id']}"
                print(f"Stopping rover with request to: {stop_url}")
                stop_response = requests.post(stop_url)
                print(f"Stop response: {stop_response.status_code}")
            except Exception as e:
                print(f"Error stopping rover: {str(e)}")
            
            rover_state['navigation_status'] = "Completed"
            print("Navigation completed")
            print("THE PACKAGE IS DROPPED!")
            return
        
        # Convert direction string to lowercase for API call
        move_direction = next_direction.lower()
        
        # Move the rover
        try:
            # Format the URL correctly with session_id and direction
            move_url = f"{API_BASE_URL}/rover/move?session_id={rover_state['session_id']}&direction={move_direction}"
            print(f"Moving rover with request to: {move_url}")
            
            # Make the POST request to move the rover
            move_response = requests.post(move_url)
            print(f"Move response status: {move_response.status_code}")
            
            if move_response.status_code == 200:
                print(f"Move response content: {move_response.text}")
            else:
                print(f"Move request failed with status {move_response.status_code}: {move_response.text}")
                rover_state['navigation_status'] = f"Failed to move: {move_response.status_code} - {move_response.text}"
                return
        except Exception as e:
            rover_state['navigation_status'] = f"Failed: Error moving rover: {str(e)}"
            print(f"Exception moving rover: {str(e)}")
            return
        
        # Get updated rover status to update current position
        try:
            status_url = f"{API_BASE_URL}/rover/status?session_id={rover_state['session_id']}"
            print(f"Getting updated status from: {status_url}")
            status_response = requests.get(status_url)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Updated status data: {status_data}")
                
                if 'position' in status_data:
                    position = status_data['position']
                    if not isinstance(position, dict):
                        if isinstance(position, list) and len(position) >= 2:
                            position = {'x': position[0], 'y': position[1]}
                        else:
                            position = {'x': 0, 'y': 0}
                    rover_state['current_position'] = position
                    print(f"Updated position after move: {position}")
            else:
                print(f"Failed to get updated status: {status_response.status_code}")
        except Exception as e:
            print(f"Error getting updated status: {str(e)}")
        
        # Wait a bit before making the next move
        time.sleep(1.5)
        
        # Recursively call auto_navigate with the new direction
        print(f"Recursively calling auto_navigate with direction: {next_direction}")
        auto_navigate(next_direction)
    except Exception as e:
        print(f"Exception in auto_navigate: {str(e)}")
        rover_state['navigation_status'] = f"Failed: {str(e)}"
        import traceback
        traceback.print_exc()

# Get auto-navigation status
@app.route('/auto-navigate/status', methods=['GET'])
def get_auto_navigation_status():
    """Get the current status of auto-navigation."""
    result = {
        "status": rover_state['navigation_status'],
        "battery_level": None  # Default to None
    }
    
    # Fetch battery level if available
    if rover_state['session_id']:
        try:
            status_url = f"{API_BASE_URL}/rover/status?session_id={rover_state['session_id']}"
            response = requests.get(status_url, timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                
                # Extract battery level
                if 'battery' in status_data:
                    bat_data = status_data['battery']
                    if isinstance(bat_data, dict) and 'level' in bat_data:
                        result['battery_level'] = bat_data['level']
                    elif isinstance(bat_data, (int, float)):
                        result['battery_level'] = bat_data
                
                # Add current position if available
                if 'position' in status_data:
                    position = status_data['position']
                    if not isinstance(position, dict):
                        if isinstance(position, list) and len(position) >= 2:
                            position = {'x': position[0], 'y': position[1]}
                    result['current_position'] = position
                elif rover_state['current_position']:
                    result['current_position'] = rover_state['current_position']
        except Exception as e:
            print(f"Error getting status for auto-navigation: {str(e)}")
    
    # Add any additional fields if we have them
    if rover_state['initial_position']:
        result['initial_position'] = rover_state['initial_position']
    if rover_state['final_position']:
        result['final_position'] = rover_state['final_position']
    
    return jsonify(result)

# Get stored position data
@app.route('/position-data', methods=['GET'])
def get_position_data():
    """Get stored initial and final position data."""
    return jsonify({
        "initial_position": rover_state['initial_position'],
        "final_position": rover_state['final_position'],
        "current_position": rover_state['current_position']
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)