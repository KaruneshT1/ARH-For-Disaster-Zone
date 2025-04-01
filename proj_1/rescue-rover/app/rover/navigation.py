import math
import time

class Navigator:
    def __init__(self):
        self.position = (0, 0)  # Starting position
        self.velocity = [0, 0]
        self.last_update_time = None
        self.obstacles = []
        self.visited_areas = set()
        
    def update_position(self, sensor_data):
        """Update position using accelerometer data (no GPS)"""
        if 'accelerometer' not in sensor_data:
            return
            
        accel = sensor_data['accelerometer']
        current_time = time.time()
        
        if self.last_update_time:
            dt = current_time - self.last_update_time
            
            # Simple dead reckoning
            self.velocity[0] += accel['x'] * dt
            self.velocity[1] += accel['y'] * dt
            
            self.position = (
                self.position[0] + self.velocity[0] * dt,
                self.position[1] + self.velocity[1] * dt
            )
            
        self.last_update_time = current_time
        self.mark_visited_area()
        
    def detect_obstacles(self, sensor_data):
        """Detect obstacles using ultrasonic sensors"""
        if 'ultrasonic' in sensor_data:
            distance = sensor_data['ultrasonic'].get('distance', 1000)
            if distance < 50:  # Less than 50cm is an obstacle
                # Calculate obstacle position based on rover orientation
                # Add to obstacles list
                pass
