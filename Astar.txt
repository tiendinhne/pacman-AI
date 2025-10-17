def astar(start_state, is_goal, successors, heuristic):
    from heapq import heappush, heappop

    open_set = []
    heappush(open_set, (heuristic(start_state), 0, start_state))  # (f, g, state)
    came_from = {}
    g_score = {start_state: 0}
    closed_set = set()

    nodes_expanded = 0
    max_frontier_size = 1

    while open_set:
        # 1 Lấy node có f nhỏ nhất
        f, g, current = heappop(open_set)
        nodes_expanded += 1

        # 2 Nếu là goal → kết thúc
        if is_goal(current):
            return reconstruct_path(came_from, current), {
                "nodes_expanded": nodes_expanded,
                "max_frontier_size": max_frontier_size
            }

        # 3 Bỏ qua nếu đã thăm
        if current in closed_set:
            continue
        closed_set.add(current)

        # 4 Sinh successor
        for next_state, cost in successors(current):
            tentative_g = g_score[current] + cost
            if next_state not in g_score or tentative_g < g_score[next_state]:
                g_score[next_state] = tentative_g
                f_score = tentative_g + heuristic(next_state)
                came_from[next_state] = current
                heappush(open_set, (f_score, tentative_g, next_state))

        max_frontier_size = max(max_frontier_size, len(open_set))

    return None, {
        "nodes_expanded": nodes_expanded,
        "max_frontier_size": max_frontier_size
    }

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return list(reversed(path))
