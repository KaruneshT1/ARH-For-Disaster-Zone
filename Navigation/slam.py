import numpy as np
import heapq
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
        self.goal = None  # Destination coordinates
        self.path = []  # Path calculated using Dijkstra’s Algorithm

        logging.info(f"SLAM system initialized with map size {map_size}")

    def update_map(self, sensor_data, position, angle):
        """
        Update the map based on sensor data. Marks detected obstacles and updates rover position.
        """
        try:
            if not (isinstance(sensor_data, list) and isinstance(position, tuple) and isinstance(angle, (int, float))):
                raise SLAMError("Invalid input data format for SLAM update.")

            x, y = position
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

    def set_goal(self, goal_position):
        """Sets the goal position for path planning."""
        if not (isinstance(goal_position, tuple) and len(goal_position) == 2):
            raise SLAMError("Goal position must be a tuple (x, y).")

        if not (0 <= goal_position[0] < self.map.shape[0] and 0 <= goal_position[1] < self.map.shape[1]):
            raise SLAMError("Goal position is out of map bounds.")

        self.goal = goal_position
        logging.info(f"Goal set to {goal_position}")

    def dijkstra_path(self):
        """Implements Dijkstra's Algorithm to find the shortest path from current position to goal."""
        if not self.goal:
            raise SLAMError("Goal position not set.")

        start = self.position
        goal = self.goal
        rows, cols = self.map.shape

        # Priority queue for Dijkstra's Algorithm
        pq = [(0, start)]  # (cost, position)
        distances = {start: 0}
        prev_nodes = {start: None}
        visited = set()

        while pq:
            current_cost, current_position = heapq.heappop(pq)
            if current_position in visited:
                continue
            visited.add(current_position)

            if current_position == goal:
                break  # Shortest path found

            x, y = current_position
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4-directional movement
                next_pos = (x + dx, y + dy)
                if 0 <= next_pos[0] < rows and 0 <= next_pos[1] < cols and self.map[next_pos] == 0:
                    new_cost = current_cost + 1  # Uniform cost for each movement
                    if next_pos not in distances or new_cost < distances[next_pos]:
                        distances[next_pos] = new_cost
                        prev_nodes[next_pos] = current_position
                        heapq.heappush(pq, (new_cost, next_pos))

        # Reconstruct path from goal to start
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = prev_nodes.get(current)
        path.reverse()

        if path and path[0] == start:
            self.path = path
            logging.info(f"Path found: {path}")
        else:
            logging.error("No valid path found.")
            self.path = []

    def move_to_next_position(self):
        """Moves the rover along the planned path. If blocked, it triggers autonomous decision-making."""
        if not self.path:
            logging.warning("No path available. Rover cannot move.")
            return

        next_position = self.path.pop(0)
        if self.map[next_position] == 1:
            logging.warning(f"Path blocked at {next_position}. Autonomous decision required.")
            self.autonomous_decision()
        else:
            self.position = next_position
            logging.info(f"Rover moved to {next_position}")

    def autonomous_decision(self):
        """Handles obstacle avoidance when the planned path is blocked (placeholder)."""
        logging.info("Autonomous decision-making triggered. (Implementation pending integration with ultrasonic)")
        # TODO: Implement real-time decision-making using ultrasonic data

    def send_data(self):
        """Prepares rover data for transmission."""
        data = {
            "position": self.position,
            "orientation": self.orientation,
            "goal": self.goal,
            "obstacles": np.argwhere(self.map == 1).tolist(),
            "path": self.path
        }
        logging.info(f"Data transmission: {data}")
        return data

    def display_map(self):
        """Displays the SLAM map."""
        try:
            if self.map.size == 0:
                raise SLAMError("SLAM map is empty. Cannot display.")

            for row in self.map:
                print(" ".join(str(int(cell)) for cell in row))

        except SLAMError as e:
            logging.error(f"SLAM Display Error: {str(e)}")
