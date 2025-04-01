from flask import Flask, jsonify
from ARH.Navigation.navigation import RoverNavigation
from ARH.Navigation.api_comm import APIComm

app = Flask(__name__)

# Initialize APIComm to start a session
api_comm = APIComm()

# Start a session and get session_id
session_id = api_comm.start_session()

# Initialize the rover with session ID and rover ID
rover_id = "Rover1"  # Example rover ID
rover_navigation = RoverNavigation(session_id, rover_id, api_comm)

@app.route('/move_forward', methods=['POST'])
def move_forward():
    rover_navigation.move_forward()
    return jsonify({"message": "Rover moving forward."})

@app.route('/move_backward', methods=['POST'])
def move_backward():
    rover_navigation.move_backward()
    return jsonify({"message": "Rover moving backward."})

@app.route('/move_left', methods=['POST'])
def move_left():
    rover_navigation.move_left()
    return jsonify({"message": "Rover moving left."})

@app.route('/move_right', methods=['POST'])
def move_right():
    rover_navigation.move_right()
    return jsonify({"message": "Rover moving right."})

@app.route('/get_sensor_data', methods=['GET'])
def get_sensor_data():
    sensor_data = rover_navigation.get_sensor_data()
    return jsonify(sensor_data)

if __name__ == '__main__':
    app.run(debug=True)
