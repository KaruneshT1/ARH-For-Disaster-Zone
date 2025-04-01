import heapq

def dijkstra_path(map, start, goal):
    """Implements Dijkstra's Algorithm to find the shortest path from current position to goal."""
    rows, cols = map.shape

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
            if 0 <= next_pos[0] < rows and 0 <= next_pos[1] < cols and map[next_pos] == 0:
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

    return path
