from ARH.Navigation.sensor_handler import SensorHandler
from ARH.Navigation.api_comm import APIComm  # Assuming the API communication is in api_comm.py

class RoverNavigation:
    def __init__(self, session_id, rover_id="Rover1"):
        self.session_id = session_id
        self.rover_id = rover_id
        self.api = APIComm(session_id, rover_id)  # APIComm is initialized with session_id and rover_id
        self.sensor_handler = SensorHandler(session_id, rover_id)

    def move_forward(self):
        """Move rover forward if no survivor detected"""
        if not self.sensor_handler.detect_survivor():
            print("Moving forward...")
            self.api.move_rover("forward")
        else:
            print("Survivor detected! Stopping rover.")
            self.api.stop_rover()

    def move_backward(self):
        """Move rover backward if no survivor detected"""
        if not self.sensor_handler.detect_survivor():
            print("Moving backward...")
            self.api.move_rover("backward")
        else:
            print("Survivor detected! Stopping rover.")
            self.api.stop_rover()

    def move_left(self):
        """Move rover left if no survivor detected"""
        if not self.sensor_handler.detect_survivor():
            print("Moving left...")
            self.api.move_rover("left")
        else:
            print("Survivor detected! Stopping rover.")
            self.api.stop_rover()

    def move_right(self):
        """Move rover right if no survivor detected"""
        if not self.sensor_handler.detect_survivor():
            print("Moving right...")
            self.api.move_rover("right")
        else:
            print("Survivor detected! Stopping rover.")
            self.api.stop_rover()
