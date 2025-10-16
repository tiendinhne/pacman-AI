from utils import bfs_distance, compute_mst_weight

# === Heuristic 1: Đơn giản ===
def heuristic_simple(state):
    """
    Heuristic rất cơ bản: chỉ đếm số lượng thức ăn chưa ăn.
    Số bit '1' trong foods_mask = số lượng thức ăn còn lại.
    """
    return bin(state.foods_mask).count("1")


# === Heuristic 2: Khoảng cách đến thức ăn gần nhất ===
def heuristic_food_distance(state, foods_list, walls):
    """
    Ước lượng chi phí = khoảng cách BFS ngắn nhất
    từ vị trí Pacman tới viên thức ăn gần nhất.
    """
    pac_pos = state.pos

    # Danh sách thức ăn chưa ăn
    remaining_foods = [
        food for i, food in enumerate(foods_list)
        if (state.foods_mask >> i) & 1
    ]

    if not remaining_foods:
        return 0

    # Kiểm tra walls là set, nếu chưa thì tạo tạm
    if not isinstance(walls, set):
        walls = {(y, x) for y, row in enumerate(walls) for x, ch in enumerate(row) if ch == '%'}

    # Tính khoảng cách BFS ngắn nhất đến một food
    min_dist = float('inf')
    for food in remaining_foods:
        dist = bfs_distance(pac_pos, food, walls)
        if dist < min_dist:
            min_dist = dist

    return min_dist


# === Heuristic 3: Kết hợp BFS + MST ===
def heuristic_food_mst(state, foods_list, walls):
    """
    Ước lượng chi phí = 
        khoảng cách đến viên thức ăn gần nhất +
        tổng trọng số MST của các viên thức ăn còn lại.
    """
    pac_pos = state.pos

    remaining_foods = [
        food for i, food in enumerate(foods_list)
        if (state.foods_mask >> i) & 1
    ]

    if not remaining_foods:
        return 0

    if not isinstance(walls, set):
        walls = {(y, x) for y, row in enumerate(walls) for x, ch in enumerate(row) if ch == '%'}

    dist_to_nearest = min(bfs_distance(pac_pos, food, walls) for food in remaining_foods)
    mst_weight = compute_mst_weight(remaining_foods, walls)

    return dist_to_nearest + mst_weight
