import numpy as np
import logging

# Set up logging
logging.basicConfig(filename='slam.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SLAMError(Exception):
    """Custom exception for SLAM failures."""
    pass

class RoverSLAM:
    def __init__(self, map_size=(50, 50)):
        """
        Initialize the SLAM system with a map of given size (default 50x50 grid).
        The grid map stores the environment (0 for free space, 1 for obstacles).
        """
        if not (isinstance(map_size, tuple) and len(map_size) == 2 and all(isinstance(i, int) and i > 0 for i in map_size)):
            raise SLAMError("Invalid map size. Must be a tuple of two positive integers.")

        self.map = np.zeros(map_size)  # Initialize map with free spaces (0s)
        self.position = (map_size[0] // 2, map_size[1] // 2)  # Start at the center
        self.orientation = 0  # Rover's initial orientation (angle in degrees)

        logging.info(f"SLAM system initialized with map size {map_size}")

    def update_map(self, sensor_data, position, angle):
        """
        Update the map based on sensor data. Marks detected obstacles and updates rover position.
        Assumes sensor data includes distance and angle.
        """
        try:
            if not (isinstance(sensor_data, list) and isinstance(position, tuple) and isinstance(angle, (int, float))):
                raise SLAMError("Invalid input data format for SLAM update.")

            x, y = position  # Rover's current position on the grid

            if not (0 <= x < self.map.shape[0] and 0 <= y < self.map.shape[1]):
                raise SLAMError(f"Invalid position {position}. Out of map bounds.")

            self.position = position
            self.orientation = angle
            logging.info(f"Updated SLAM position: {position}, Orientation: {angle}")

            for sensor in sensor_data:
                if not isinstance(sensor, dict) or 'distance' not in sensor or 'angle' not in sensor:
                    raise SLAMError("Sensor data must be a list of dictionaries with 'distance' and 'angle' keys.")

                distance = sensor['distance']
                sensor_angle = sensor['angle']

                if not (isinstance(distance, (int, float)) and distance >= 0):
                    raise SLAMError(f"Invalid distance value: {distance}")

                obstacle_x = x + int(distance * np.cos(np.radians(sensor_angle)))
                obstacle_y = y + int(distance * np.sin(np.radians(sensor_angle)))

                if 0 <= obstacle_x < self.map.shape[0] and 0 <= obstacle_y < self.map.shape[1]:
                    self.map[obstacle_x][obstacle_y] = 1  # Mark obstacle
                    logging.info(f"Obstacle detected at ({obstacle_x}, {obstacle_y})")

        except SLAMError as e:
            logging.error(f"SLAM Update Error: {str(e)}")

    def display_map(self):
        """
        Display the current map (for debugging purposes).
        0 represents free space, 1 represents obstacles.
        """
        try:
            if self.map.size == 0:
                raise SLAMError("SLAM map is empty. Cannot display.")

            for row in self.map:
                print(" ".join(str(int(cell)) for cell in row))

        except SLAMError as e:
            logging.error(f"SLAM Display Error: {str(e)}")
