import heapq
import math

def astar(start, goal, obstacles=None):
    """
    A* pathfinding algorithm implementation.
    
    Args:
        start: Tuple (x, y) representing start position
        goal: Tuple (x, y) representing goal position
        obstacles: Set of tuples representing obstacle positions (optional)
    
    Returns:
        List of tuples representing the path from start to goal
    """
    # Validate input parameters
    if not isinstance(start, tuple) or len(start) != 2:
        raise ValueError(f"Start position must be a tuple of (x,y), got {start}")
        
    if not isinstance(goal, tuple) or len(goal) != 2:
        raise ValueError(f"Goal position must be a tuple of (x,y), got {goal}")
    
    print(f"A* pathfinding from {start} to {goal}")
    
    # If start and goal are the same, return a path with just that position
    if start == goal:
        print("Start and goal are the same position, returning direct path")
        return [start]
    
    if obstacles is None:
        obstacles = set()
    
    # Helper function to calculate heuristic (Euclidean distance)
    def heuristic(a, b):
        return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
    
    # Initialize open and closed sets
    open_set = []
    closed_set = set()
    came_from = {}
    
    # Initialize g and f scores
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    # Add start node to open set
    heapq.heappush(open_set, (f_score[start], start))
    
    # Main loop
    while open_set:
        # Get the node with the lowest f_score
        current_f, current = heapq.heappop(open_set)
        
        # If we've reached the goal, reconstruct and return the path
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path = path[::-1]  # Reverse the path
            print(f"Path found with {len(path)} steps from {path[0]} to {path[-1]}")
            return path
        
        # Add current node to closed set
        closed_set.add(current)
        
        # Define possible moves (up, down, left, right, and diagonals)
        neighbors = [
            (current[0]+1, current[1]),    # right
            (current[0]-1, current[1]),    # left
            (current[0], current[1]+1),    # up
            (current[0], current[1]-1),    # down
            (current[0]+1, current[1]+1),  # diagonal: up-right
            (current[0]-1, current[1]+1),  # diagonal: up-left
            (current[0]+1, current[1]-1),  # diagonal: down-right
            (current[0]-1, current[1]-1),  # diagonal: down-left
        ]
        
        for neighbor in neighbors:
            # Skip if the neighbor is in the closed set or is an obstacle
            if neighbor in closed_set or neighbor in obstacles:
                continue
            
            # Calculate tentative g_score
            # Use 1.414 (√2) for diagonal movement, 1.0 for orthogonal
            if abs(neighbor[0] - current[0]) == 1 and abs(neighbor[1] - current[1]) == 1:
                # Diagonal movement
                tentative_g = g_score.get(current, float('inf')) + 1.414
            else:
                # Orthogonal movement
                tentative_g = g_score.get(current, float('inf')) + 1.0
            
            # If this is not a better path, skip
            if neighbor in g_score and tentative_g >= g_score[neighbor]:
                continue
            
            # This path is the best so far, record it
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g
            f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
            
            # Add to open set if not already there
            if neighbor not in [i[1] for i in open_set]:
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    # If we get here, there's no path to the goal
    print(f"No path found from {start} to {goal}")
    return None

# Example usage: a simple test case
if __name__ == "__main__":
    # Define start and goal positions
    start = (0, 0)
    goal = (5, 5)
    
    # Define obstacles
    obstacles = {(2, 2), (2, 3), (3, 2), (3, 3)}
    
    # Calculate path
    path = astar(start, goal, obstacles)
    
    print("A* Path:", path)
