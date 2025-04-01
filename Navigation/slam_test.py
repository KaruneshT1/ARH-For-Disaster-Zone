import time
import os
from slam import RoverSLAM

if __name__ == "__main__":
    # Create an instance of RoverSLAM with a map size of 20x20
    slam = RoverSLAM(map_size=(20, 20))

    slam.position = (5, 2)  # Set rover's position to (5, 5)

    # Manually set obstacles (locations where the rover cannot move)
    obstacles = [(5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5)]
    slam.set_obstacles(obstacles)

    # Set the goal position for the rover to reach
    slam.set_goal((15, 15))

    # Plan the path from current position to goal using Dijkstra's Algorithm
    slam.dijkstra_path()

    # Display the initial map (with obstacles, rover, goal, and path)
    slam.display_map()

    # Start simulating the rover's movement along the path step-by-step
    slam.simulate_movement(delay=0.3)  # You can adjust delay for slower/faster movement
