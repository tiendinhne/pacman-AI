
from collections import deque
import heapq

def bfs_distance(start, goal, walls):
    """Tính khoảng cách ngắn nhất giữa hai điểm trên lưới (bỏ qua tường)."""
    if start == goal:
        return 0

    queue = deque([(start, 0)])
    visited = {start}

    while queue:
        (x, y), dist = queue.popleft()
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            next_pos = (nx, ny)

            if next_pos in visited or next_pos in walls:
                continue
            if next_pos == goal:
                return dist + 1

            queue.append((next_pos, dist + 1))
            visited.add(next_pos)

    return float('inf')


def compute_mst_weight(nodes, walls):
    """Tính tổng trọng số của Minimum Spanning Tree (Prim)."""
    if not nodes:
        return 0

    start = nodes[0]
    visited = {start}
    edges = []

    for node in nodes[1:]:
        dist = bfs_distance(start, node, walls)
        heapq.heappush(edges, (dist, node))

    total_weight = 0

    while len(visited) < len(nodes) and edges:
        dist, next_node = heapq.heappop(edges)
        if next_node in visited:
            continue

        total_weight += dist
        visited.add(next_node)

        for node in nodes:
            if node not in visited:
                new_dist = bfs_distance(next_node, node, walls)
                heapq.heappush(edges, (new_dist, node))

    return total_weight

