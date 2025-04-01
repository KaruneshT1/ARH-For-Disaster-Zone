# app.py
from flask import Flask, render_template, jsonify, request
import threading
import time
import logging
from app.api.rover_api import RoverAPI
from app.rover.battery_manager import BatteryManager  # Assuming this is where BatteryManager is defined

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname%s - %(message)s')
logger = logging.getLogger('rover_app')

app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

# Initialize components
rover_api = RoverAPI()
battery_manager = BatteryManager()

# Global state
rover_state = {
    "status": "initializing",
    "battery_level": 100,
    "position": {"x": 0, "y": 0},
    "orientation": 0,
    "is_moving": False,
    "current_direction": None,
    "is_charging": False,
    "has_communication": True,
    "last_updated": time.time(),
    "mission_time": 0,
    "mission_start_time": time.time(),
    "sensor_data": {},
    "errors": []
}

# Flag to indicate if background thread is running
background_thread_running = False

def background_task():
    """Background task to periodically update rover state"""
    global background_thread_running
    
    logger.info("Starting background task")
    
    # Start a session
    session_id = rover_api.start_session()
    if not session_id:
        logger.error("Failed to start session. Background task stopping.")
        rover_state["errors"].append("Failed to start API session")
        background_thread_running = False
        return
        
    logger.info(f"Session started with ID: {session_id}")
    
    try:
        while background_thread_running:
            try:
                # Update mission time
                rover_state["mission_time"] = int(time.time() - rover_state["mission_start_time"])
                
                # Get rover status
                status = rover_api.get_rover_status()
                if "error" in status:
                    logger.warning(f"Error getting rover status: {status['error']}")
                    rover_state["errors"].append(f"API error: {status['error']}")
                    time.sleep(5)  # Wait before retrying
                    continue
                    
                # Update battery and check constraints
                if "battery_level" in status:
                    battery_level = status["battery_level"]
                    rover_state["battery_level"] = battery_level
                    
                    # Update battery manager
                    state_changed = battery_manager.update_battery_level(battery_level)
                    rover_state["is_charging"] = battery_manager.is_charging
                    rover_state["has_communication"] = battery_manager.has_communication
                    
                    # If charging, stop the rover
                    if rover_state["is_charging"] and rover_state["is_moving"]:
                        logger.info("Rover is charging - stopping movement")
                        rover_api.stop_rover()
                        rover_state["is_moving"] = False
                        rover_state["current_direction"] = None
                
                # If we have communication, get sensor data
                if rover_state["has_communication"]:
                    sensor_data = rover_api.get_sensor_data()
                    if "error" not in sensor_data:
                        rover_state["sensor_data"] = sensor_data
                        
                        # Update position if available in sensor data (simulated for demo)
                        if "accelerometer" in sensor_data:
                            # This is simplified - in a real app you'd use dead reckoning
                            accel = sensor_data["accelerometer"]
                            rover_state["position"]["x"] += accel.get("x", 0) * 0.1
                            rover_state["position"]["y"] += accel.get("y", 0) * 0.1
                
                rover_state["last_updated"] = time.time()
                
                # Sleep for a short period to avoid overwhelming API
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in background task: {str(e)}")
                rover_state["errors"].append(f"Background task error: {str(e)}")
                time.sleep(5)  # Wait before retrying
    finally:
        if session_id:
            rover_api.end_session(session_id)
        logger.info("Background task stopping")

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/start')
def start_rover():
    """Start the rover background task"""
    global background_thread_running
    
    if not background_thread_running:
        background_thread_running = True
        rover_state["mission_start_time"] = time.time()
        rover_state["status"] = "starting"
        
        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({"status": "started"})
    else:
        return jsonify({"status": "already running"})

@app.route('/api/stop')
def stop_rover():
    """Stop the rover background task"""
    global background_thread_running
    
    if background_thread_running:
        background_thread_running = False
        rover_api.stop_rover()  # Make sure rover stops moving
        rover_state["status"] = "stopped"
        rover_state["is_moving"] = False
        
        return jsonify({"status": "stopped"})
    else:
        return jsonify({"status": "not running"})

@app.route('/api/status')
def get_status():
    """Get the current rover state"""
    return jsonify(rover_state)

@app.route('/api/control', methods=['POST'])
def control_rover():
    """Send a control command to the rover"""
    if not rover_state["has_communication"]:
        return jsonify({"error": "No communication with rover", "success": False})
        
    if rover_state["is_charging"]:
        return jsonify({"error": "Cannot move rover while charging", "success": False})
        
    command = request.json.get('command')
    
    if command == 'stop':
        result = rover_api.stop_rover()
        if "error" not in result:
            rover_state["is_moving"] = False
            rover_state["current_direction"] = None
            return jsonify({"status": "Rover stopped", "success": True})
        else:
            return jsonify({"error": result["error"], "success": False})
            
    elif command in ['forward', 'backward', 'left', 'right']:
        result = rover_api.move_rover(command)
        if "error" not in result:
            rover_state["is_moving"] = True
            rover_state["current_direction"] = command
            return jsonify({"status": f"Rover moving {command}", "success": True})
        else:
            return jsonify({"error": result["error"], "success": False})
            
    return jsonify({"error": "Invalid command", "success": False})

@app.route('/api/test-connection')
def test_connection():
    """Test connection to all API endpoints"""
    test_api = RoverAPI()
    results = test_api.test_connection()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
