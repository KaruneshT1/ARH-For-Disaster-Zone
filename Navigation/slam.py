import numpy as np
import logging
import time
import os
from pathfinding import dijkstra_path  # Import the new dijkstra_path function

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
        self.goals = []  # List of goal positions
        self.path = []  # Path calculated using Dijkstra’s Algorithm

        logging.info(f"SLAM system initialized with map size {map_size}")

    def set_obstacles(self, obstacle_positions):
        """Manually set obstacles on the map for testing."""
        for obs in obstacle_positions:
            if 0 <= obs[0] < self.map.shape[0] and 0 <= obs[1] < self.map.shape[1]:
                self.map[obs] = 1

    def set_goals(self, goal_positions):
        """Sets multiple goal positions for path planning."""
        if not isinstance(goal_positions, list) or not all(isinstance(goal, tuple) and len(goal) == 2 for goal in goal_positions):
            raise SLAMError("Goal positions must be a list of tuples (x, y).")
        
        self.goals = goal_positions
        logging.info(f"Goals set to {self.goals}")

    def find_nearest_goal(self):
        """Find the nearest goal from the current position using Dijkstra’s Algorithm."""
        if not self.goals:
            raise SLAMError("No goals set.")
        
        nearest_goal = None
        shortest_distance = float('inf')
        for goal in self.goals:
            path = dijkstra_path(self.map, self.position, goal)
            if path:
                distance = len(path)
                if distance < shortest_distance:
                    shortest_distance = distance
                    nearest_goal = goal
        
        if nearest_goal is not None:
            return nearest_goal
        else:
            return None

    def dijkstra_path(self):
        """Uses the dijkstra_path function from pathfinding.py to find the shortest path."""
        if not self.goals:
            raise SLAMError("Goal positions not set.")
        
        # Find nearest goal
        nearest_goal = self.find_nearest_goal()
        if not nearest_goal:
            logging.error("No valid path found to any goal.")
            self.path = []
            return
        
        self.path = dijkstra_path(self.map, self.position, nearest_goal)
        if self.path:
            logging.info(f"Path found to nearest goal: {self.path}")
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

        # If the rover reaches the current goal, remove it from the list of goals
        if self.position == self.goals[0]:
            self.goals.pop(0)
            logging.info(f"Reached goal {self.position}. Remaining goals: {self.goals}")

        return True

    def display_map(self):
        """Displays the SLAM map with obstacles, rover, goals, and path."""
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal screen

        display_grid = np.full(self.map.shape, '.', dtype=str)

        # Mark obstacles
        obstacle_positions = np.argwhere(self.map == 1)
        for x, y in obstacle_positions:
            display_grid[x, y] = '#'

        # Mark path
        for px, py in self.path:
            display_grid[px, py] = '*'

        # Mark rover and goals
        x, y = self.position
        display_grid[x, y] = 'R'
        for gx, gy in self.goals:
            display_grid[gx, gy] = 'G'

        # Print the map
        for row in display_grid:
            print(" ".join(row))
        print("\n")

    def simulate_movement(self, delay=0.5):
        """Simulates rover movement step by step with visualization."""
        while self.goals:
            # If there are no goals left, stop
            if not self.goals:
                logging.info("All goals reached!")
                break

            self.dijkstra_path()  # Plan the path to the next goal
            
            while self.move_to_next_position():
                self.display_map()
                time.sleep(delay)

            # If no path is found to the goal, break out of the simulation
            if not self.path:
                logging.error("Unable to find a path to the goal. Stopping.")
                break
