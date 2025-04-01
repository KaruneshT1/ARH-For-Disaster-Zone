# rover_api.py
import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('rover_api')

class RoverAPI:
    def __init__(self):
        # Base URL from the challenge documentation
        self.base_url = "https://roverdata2-production.up.railway.app"
        self.session_id = None
        self.last_request_time = 0
        self.request_interval = 0.5  # Limit requests to at most 2 per second
        
    def _rate_limit(self):
        """Simple rate limiting to avoid overwhelming the API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_interval:
            time.sleep(self.request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def start_session(self):
        """Start a new session with the rover API"""
        self._rate_limit()
        try:
            logger.info("Starting new rover API session")
            response = requests.post(f"{self.base_url}/api/session/start")
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                logger.info(f"Session started successfully with ID: {self.session_id}")
                return self.session_id
            else:
                logger.error(f"Failed to start session. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exception during session start: {str(e)}")
            return None
            
    def get_fleet_status(self):
        """Get status of all rovers in the fleet"""
        if not self.session_id:
            logger.warning("Cannot get fleet status: No active session")
            return {"error": "No active session"}
            
        self._rate_limit()
        try:
            logger.info("Getting fleet status")
            response = requests.get(f"{self.base_url}/api/fleet/status?session_id={self.session_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get fleet status. Status code: {response.status_code}")
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Exception getting fleet status: {str(e)}")
            return {"error": str(e)}
    
    def get_rover_status(self):
        """Get status of Rover-1"""
        if not self.session_id:
            logger.warning("Cannot get rover status: No active session")
            return {"error": "No active session"}
            
        self._rate_limit()
        try:
            logger.info("Getting rover status")
            response = requests.get(f"{self.base_url}/api/rover/Rover-1/status?session_id={self.session_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get rover status. Status code: {response.status_code}")
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Exception getting rover status: {str(e)}")
            return {"error": str(e)}
    
    def get_sensor_data(self):
        """Get sensor data from Rover-1"""
        if not self.session_id:
            logger.warning("Cannot get sensor data: No active session")
            return {"error": "No active session"}
            
        self._rate_limit()
        try:
            logger.info("Getting sensor data")
            response = requests.get(f"{self.base_url}/api/rover/Rover-1/sensor-data?session_id={self.session_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get sensor data. Status code: {response.status_code}")
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Exception getting sensor data: {str(e)}")
            return {"error": str(e)}
    
    def move_rover(self, direction):
        """Move the rover in the specified direction"""
        if not self.session_id:
            logger.warning("Cannot move rover: No active session")
            return {"error": "No active session"}
            
        if direction not in ["forward", "backward", "left", "right"]:
            logger.warning(f"Invalid direction: {direction}")
            return {"error": "Invalid direction"}
            
        self._rate_limit()
        try:
            logger.info(f"Moving rover {direction}")
            response = requests.post(
                f"{self.base_url}/api/rover/Rover-1/move?session_id={self.session_id}&direction={direction}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to move rover. Status code: {response.status_code}")
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Exception moving rover: {str(e)}")
            return {"error": str(e)}
    
    def stop_rover(self):
        """Stop the rover's movement"""
        if not self.session_id:
            logger.warning("Cannot stop rover: No active session")
            return {"error": "No active session"}
            
        self._rate_limit()
        try:
            logger.info("Stopping rover")
            response = requests.post(f"{self.base_url}/api/rover/Rover-1/stop?session_id={self.session_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to stop rover. Status code: {response.status_code}")
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Exception stopping rover: {str(e)}")
            return {"error": str(e)}
            
    def test_connection(self):
        """Test all API endpoints and return results"""
        results = {}
        
        # Test 1: Start session
        session_id = self.start_session()
        results["session"] = {
            "success": session_id is not None,
            "session_id": session_id
        }
        
        if session_id:
            # Test 2: Get fleet status
            fleet_status = self.get_fleet_status()
            results["fleet_status"] = {
                "success": "error" not in fleet_status,
                "response": fleet_status
            }
            
            # Test 3: Get rover status
            rover_status = self.get_rover_status()
            results["rover_status"] = {
                "success": "error" not in rover_status,
                "response": rover_status
            }
            
            # Test 4: Get sensor data
            sensor_data = self.get_sensor_data()
            results["sensor_data"] = {
                "success": "error" not in sensor_data,
                "response": sensor_data
            }
            
            # Test 5: Move rover
            move_result = self.move_rover("forward")
            results["move_rover"] = {
                "success": "error" not in move_result,
                "response": move_result
            }
            
            # Test 6: Stop rover
            stop_result = self.stop_rover()
            results["stop_rover"] = {
                "success": "error" not in stop_result,
                "response": stop_result
            }
        
        return results
