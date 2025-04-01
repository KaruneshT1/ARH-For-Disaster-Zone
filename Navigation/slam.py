import numpy as np
import heapq
import logging
import time
import os

# Set up logging
logging.basicConfig(filename='slam.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SLAMError(Exception):
    """Custom exception for SLAM failures."""
    pass

class RoverSLAM:
    def __init__(self, map_size=(20, 20)):
        """
        Initialize the SLAM system with a map of given size (default 20x20 grid).
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

    def set_obstacles(self, obstacle_positions):
        """Manually set obstacles on the map for testing."""
        for obs in obstacle_positions:
            if 0 <= obs[0] < self.map.shape[0] and 0 <= obs[1] < self.map.shape[1]:
                self.map[obs] = 1

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
                    new_cost = current_cost + 1
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
            self.path = path[1:]  # Remove starting position
            logging.info(f"Path found: {path}")
        else:
            logging.error("No valid path found.")
            self.path = []

    def move_to_next_position(self):
        """Moves the rover along the planned path, updating the map display."""
        if not self.path:
            logging.warning("No path available. Rover cannot move.")
            return False

        self.position = self.path.pop(0)
        logging.info(f"Rover moved to {self.position}")
        return True

    def display_map(self):
        """Displays the SLAM map with obstacles, rover, goal, and path."""
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal screen

        display_grid = np.full(self.map.shape, '.', dtype=str)

        # Mark obstacles
        obstacle_positions = np.argwhere(self.map == 1)
        for x, y in obstacle_positions:
            display_grid[x, y] = '#'

        # Mark path
        for px, py in self.path:
            display_grid[px, py] = '*'

        # Mark rover and goal
        x, y = self.position
        display_grid[x, y] = 'R'
        if self.goal:
            gx, gy = self.goal
            display_grid[gx, gy] = 'G'

        # Print the map
        for row in display_grid:
            print(" ".join(row))
        print("\n")

    def simulate_movement(self, delay=0.5):
        """Simulates rover movement step by step with visualization."""
        while self.move_to_next_position():
            self.display_map()
            time.sleep(delay)
