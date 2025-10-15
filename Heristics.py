
from collections import deque
def heuristic_simple(state):
    return len(state.foods)

def bfs_distance(start, goal, walls):

    if start == goal:
        return 0

    queue = deque([(start, 0)])  # (vị trí, khoảng cách)
    visited = {start}

    while queue:
        (x, y), dist = queue.popleft()

        # Duyệt 4 hướng cơ bản
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            next_pos = (nx, ny)

            # Bỏ qua tường hoặc vị trí đã thăm
            if next_pos in visited or next_pos in walls:
                continue

            if next_pos == goal:
                return dist + 1

            queue.append((next_pos, dist + 1))
            visited.add(next_pos)

    # Không đến được
    return float('inf')

def heuristic_food_distance(state):
    pacman_pos = state.pacman
    walls = state.walls
    foods = state.foods

    # Không còn thức ăn
    if not foods:
        return 0

    # Tìm thức ăn gần nhất theo BFS
    min_dist = float('inf')
    for food in foods:
        dist = bfs_distance(pacman_pos, food, walls)
        if dist < min_dist:
            min_dist = dist

    return min_dist


