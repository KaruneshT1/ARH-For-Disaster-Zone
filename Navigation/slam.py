import numpy as np

class RoverSLAM:
    def __init__(self, map_size=(50, 50)):
        """
        Initialize the SLAM system with a map of given size (default 50x50 grid).
        The grid map will store the environment (0 for free space, 1 for obstacles).
        """
        self.map = np.zeros(map_size)  # Initialize map with all free spaces (0s)
        self.position = (25, 25)  # Start in the middle of the map (can be updated by odometry or SLAM)
        self.orientation = 0  # Rover's initial orientation (angle, in degrees)

    def update_map(self, sensor_data, position, angle):
        """
        Update the map based on sensor data. Marks the detected obstacles and updates the rover's position.
        Assumes sensor data includes distance and direction.
        """
        self.position = position
        self.orientation = angle

        for sensor in sensor_data:
            distance = sensor['distance']
            angle = sensor['angle']
            x, y = position  # Rover's current position on the grid

            # Calculate obstacle location based on distance and angle (simplified)
            obstacle_x = x + int(distance * np.cos(np.radians(angle)))
            obstacle_y = y + int(distance * np.sin(np.radians(angle)))

            if 0 <= obstacle_x < self.map.shape[0] and 0 <= obstacle_y < self.map.shape[1]:
                self.map[obstacle_x][obstacle_y] = 1  # Mark obstacle on the map

    def display_map(self):
        """
        Display the current map (for debugging purposes).
        0 represents free space, 1 represents obstacles.
        """
        for row in self.map:
            print(" ".join(str(cell) for cell in row))

