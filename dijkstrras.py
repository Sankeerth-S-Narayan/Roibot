import matplotlib.pyplot as plt
import numpy as np
import heapq

# Define the warehouse layout
# 0 = free space, 1 = obstacle
warehouse = np.array([
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0, 1, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0, 0, 1, 0, 1],
    [0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
    [0, 1, 0, 1, 1, 1, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
])

start = (0, 0)  # Starting point (top-left corner)
goal = (6, 4)   # Goal point (bottom-right corner)

# Define the possible movements (up, down, left, right)
movements = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def dijkstra(warehouse, start, goal):
    rows, cols = warehouse.shape
    distances = {node: float('inf') for node in np.ndindex(warehouse.shape)}
    distances[start] = 0
    priority_queue = [(0, start)]
    previous_nodes = {start: None}
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_node == goal:
            break
        
        if current_distance > distances[current_node]:
            continue
        
        for movement in movements:
            neighbor = (current_node[0] + movement[0], current_node[1] + movement[1])
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and warehouse[neighbor] == 0:
                distance = current_distance + 1  # Assuming uniform cost for simplicity
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))
    
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    path.reverse()
    return path

# Find the shortest path
path = dijkstra(warehouse, start, goal)

# Plot the warehouse and the path
plt.figure(figsize=(10, 10))
plt.imshow(warehouse, cmap='gray_r')

# Mark start and goal
plt.scatter(start[1], start[0], color='green', s=100, label='Start')
plt.scatter(goal[1], goal[0], color='red', s=100, label='Goal')

# Plot the path
if path:
    path_x, path_y = zip(*path)
    plt.plot(path_y, path_x, color='blue', linewidth=2, label='Path')

# Add labels
plt.title('Dijkstra Path Planning in Warehouse')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True)
plt.show()