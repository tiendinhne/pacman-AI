
import os
from dataclasses import dataclass
from typing import Tuple, Set, List, Dict

# --- QUY ƯỚC KÝ TỰ TRÊN BẢN ĐỒ ---
WALL = '%'
PACMAN = 'P'
FOOD = '.'
PIE = 'o' 
GHOST = 'G'
EXIT = 'E'
EMPTY = ' '

# --- CÁC HẰNG SỐ CỦA GAME ---
PIE_DURATION = 5

@dataclass(frozen=True, order=True)
class State:
    """
    Định nghĩa một trạng thái (State) trong game Pacman.

    `frozen=True` làm cho các đối tượng State không thể thay đổi,
    cho phép chúng được sử dụng làm key trong dictionary hoặc trong set (rất quan trọng cho các thuật toán tìm kiếm).
    `order=True` tự động tạo các phương thức so sánh, hữu ích cho hàng đợi ưu tiên.

    Attributes:
        pos (Tuple[int, int]): Tọa độ hiện tại của Pacman (y, x).
        pie_time (int): Thời gian hiệu lực còn lại của Pie.
        foods_mask (int): Bitmask đại diện cho trạng thái của các viên thức ăn.
        total_steps (int): Tổng số bước đi đã thực hiện, dùng để đồng bộ vị trí ma.
    """    
    pos: Tuple[int, int]
    pie_time: int
    foods_mask: int
    total_steps: int

def load_map(path: str) -> Tuple[
    List[List[str]], Tuple[int, int], Set[Tuple[int, int]], List[Tuple[int, int]],
    Tuple[int, int], Set[Tuple[int, int]], Dict[Tuple[int, int], int], List[Tuple[int, int]]
]:
    """
    Đọc file bản đồ .txt và trả về:
      grid (List[List[str]]), start_pos, pies_set, initial_ghosts,
      exit_pos, corners, foods_map, foods_list

    Lưu ý: ký tự theo quy ước:
      WALL = '%', PACMAN = 'P', FOOD = '.', PIE = 'o' (hỗ trợ 'O' tạm thời),
      GHOST = 'G', EXIT = 'E', EMPTY = ' '
    """
    grid: List[List[str]] = []
    start_pos = None
    pies_set: Set[Tuple[int,int]] = set()
    initial_ghosts: List[Tuple[int,int]] = []
    exit_pos = None
    temp_foods: List[Tuple[int,int]] = []

    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy file bản đồ tại: {path}")

    # --- Đọc file, giữ nguyên khoảng trắng trong dòng ---
    with open(path, 'r', encoding='utf-8') as f:
        for y, line in enumerate(f):
            clean_line = line.rstrip('\n')  # giữ khoảng trắng nếu có
            row = list(clean_line)
            grid.append(row)
            for x, ch in enumerate(row):
                pos = (y, x)
                if ch == PACMAN:
                    start_pos = pos
                elif ch == FOOD:
                    temp_foods.append(pos)
                elif ch == PIE or ch == 'O':   # chấp nhận tạm 'O' nếu file dùng in hoa
                    pies_set.add(pos)
                elif ch == GHOST:
                    initial_ghosts.append(pos)
                elif ch == EXIT:
                    exit_pos = pos
                # WALL và EMPTY không cần xử lý ở đây

    if not grid:
        raise ValueError("Bản đồ rỗng.")

    # --- Chuẩn hóa: đảm bảo mọi hàng có cùng chiều dài ---
    max_width = max(len(row) for row in grid)
    for row in grid:
        if len(row) < max_width:
            row.extend([EMPTY] * (max_width - len(row)))

    height = len(grid)
    width = max_width

    # Kiểm tra tồn tại Pacman & Exit
    if start_pos is None:
        raise ValueError("Bản đồ thiếu vị trí Pacman ('P').")
    if exit_pos is None:
        raise ValueError("Bản đồ thiếu cổng thoát ('E').")

    # --- Tính 4 góc (dùng cho teleport) ---
    # giả định có "tường" bao quanh → góc hợp lệ nằm ở (1,1), (1,width-2), ...
    corners: Set[Tuple[int,int]] = set()
    if height >= 3 and width >= 3:
        corners = {
            (1, 1), (1, width - 2),
            (height - 2, 1), (height - 2, width - 2)
        }

    # Sắp xếp danh sách food để index bitmask ổn định
    temp_foods.sort()
    foods_list = temp_foods
    foods_map = {pos: i for i, pos in enumerate(foods_list)}

    return (grid, start_pos, pies_set, initial_ghosts, exit_pos,
            corners, foods_map, foods_list)



def _calculate_ghost_paths(initial_ghosts, grid):
    paths = {}
    for start_pos in initial_ghosts:
        y, x = start_pos
        path = []

        # Di chuyển sang trái
        left = []
        for i in range(x - 1, -1, -1):
            if grid[y][i] == WALL: break
            left.append((y, i))

        # Di chuyển sang phải
        right = []
        for i in range(x + 1, len(grid[0])):
            if grid[y][i] == WALL: break
            right.append((y, i))

        # Tạo đường tuần tra: trái → start → phải → quay lại
        full_path = left[::-1] + [start_pos] + right + right[::-1] + [start_pos] + left
        if len(full_path) > 1:
            paths[start_pos] = full_path
        #else: Ghost tại {start_pos} không có đường tuần tra.
    return paths


def get_ghost_positions(
    step: int,
    initial_ghosts: List[Tuple[int, int]],
    ghost_paths: Dict[Tuple[int, int], List[Tuple[int, int]]]
) -> Set[Tuple[int, int]]:
    """Lấy vị trí của tất cả các ma tại một bước đi cụ thể."""
    positions = set()
    for ghost_start_pos in initial_ghosts:
        path = ghost_paths.get(ghost_start_pos)
        if not path: continue
        # Dùng modulo để lặp lại lộ trình tuần tra
        current_pos = path[step % len(path)]
        positions.add(current_pos)
    return positions


def is_goal(state: State, exit_pos: Tuple[int, int]) -> bool:
    """Kiểm tra trạng thái đích: ăn hết thức ăn VÀ đến được cổng thoát."""
    return state.foods_mask == 0 and state.pos == exit_pos


def successors(
    state: State, grid: List[List[str]], pies_set: Set[Tuple[int, int]],
    initial_ghosts: List[Tuple[int, int]],
    ghost_paths: Dict[Tuple[int, int], List[Tuple[int, int]]],
    foods_map: Dict[Tuple[int, int], int],
    corners: Set[Tuple[int, int]]
) -> List[Tuple[str, State, int]]:
    """
    Sinh các trạng thái kế tiếp hợp lệ. Trả về list các tuple:
      (action_str, new_state, cost)

    An toàn với mọi kích thước hàng: luôn kiểm tra biên trước khi index grid[y][x].
    """
    successors_list = []
    actions = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)}

    rows = len(grid)
    (y, x) = state.pos
    next_step = state.total_steps + 1
    ghosts_next_positions = get_ghost_positions(next_step, initial_ghosts, ghost_paths)

    # --- Di chuyển 4 hướng ---
    for action, (dy, dx) in actions.items():
        new_y, new_x = y + dy, x + dx
        new_pos = (new_y, new_x)

        # BOUNDS CHECK: kiểm tra chỉ số hàng và cột trước khi truy cập grid
        if not (0 <= new_y < rows):
            continue
        if not (0 <= new_x < len(grid[new_y])):
            continue

        # Nếu là tường và không có pie -> bỏ qua
        if grid[new_y][new_x] == WALL and state.pie_time == 0:
            continue

        # Va chạm ma (nếu không có pie)
        if state.pie_time == 0 and new_pos in ghosts_next_positions:
            continue

        # Cập nhật pie_time
        new_pie_time = max(0, state.pie_time - 1)
        if new_pos in pies_set:
            new_pie_time = PIE_DURATION

        # Cập nhật foods_mask (bitmask)
        new_foods_mask = state.foods_mask
        food_index = foods_map.get(new_pos)
        if food_index is not None and ((state.foods_mask >> food_index) & 1):
            new_foods_mask = state.foods_mask & ~(1 << food_index)

        new_state = State(new_pos, new_pie_time, new_foods_mask, next_step)
        successors_list.append((action, new_state, 1))

    # --- Teleport giữa các góc ---
    if state.pos in corners:
        all_corners = sorted(list(corners)) # Sắp xếp để có thứ tự cố định (TL, TR, BL, BR)
        
        target_corner = None
        
        if state.pos == all_corners[0]:  # Top-Left (C0) -> Bottom-Right (C3)
            target_corner = all_corners[3]
        elif state.pos == all_corners[3]:  # Bottom-Right (C3) -> Top-Left (C0)
            target_corner = all_corners[0]
        elif state.pos == all_corners[1]:  # Top-Right (C1) -> Bottom-Left (C2)
            target_corner = all_corners[2]
        elif state.pos == all_corners[2]:  # Bottom-Left (C2) -> Top-Right (C1)
            target_corner = all_corners[1]
            
        
        if target_corner:
            # Va chạm ma (nếu không có pie)
            if state.pie_time == 0 and target_corner in ghosts_next_positions:
                pass # Bỏ qua nếu có ma ở điểm đến
            else:
                # pie_time giảm 1
                new_pie_time = max(0, state.pie_time - 1)
                new_foods_mask = state.foods_mask

                new_state = State(target_corner, new_pie_time, new_foods_mask, next_step)

                # Kiểm tra tránh trùng lặp nếu teleport trùng với move bình thường (thường không xảy ra)
                if not any(s[1].pos == target_corner for s in successors_list):
                    successors_list.append((f'TELEPORT to {target_corner}', new_state, 1))

    return successors_list

def rotate_map_180(
    grid: List[str], 
    pacman_pos: Tuple[int, int], 
    pies_set: Set[Tuple[int, int]], 
    initial_ghosts: List[Tuple[int, int]],
    exit_pos: Tuple[int, int], 
    corners: Set[Tuple[int, int]],
    foods_map: Dict[Tuple[int, int], int], 
    foods_list: List[Tuple[int, int]]
) -> Tuple[
    List[str], Tuple[int, int], Set[Tuple[int, int]], List[Tuple[int, int]],
    Tuple[int, int], Set[Tuple[int, int]], Dict[Tuple[int, int], int], List[Tuple[int, int]]
]:
    """
    Xoay lưới và các tọa độ 180 độ. (y, x) -> (R - 1 - y, C - 1 - x).
    """
    R = len(grid) # Chiều cao
    C = len(grid[0]) # Chiều rộng
    
    # 1. Xoay lưới (Grid)
    # Xoay 180 độ = đảo ngược thứ tự các hàng, và đảo ngược các ký tự trong mỗi hàng.
    new_grid = [row[::-1] for row in grid[::-1]]
    
    # 2. Hàm tiện ích để xoay một tọa độ
    def rotate_coord(y, x):
        # (y, x) -> (R - 1 - y, C - 1 - x)
        new_y = R - 1 - y
        new_x = C - 1 - x
        return (new_y, new_x)

    # 3. Áp dụng cho tất cả các tọa độ
    new_pacman_pos = rotate_coord(*pacman_pos)
    new_exit_pos = rotate_coord(*exit_pos)
    
    new_pies_set = {rotate_coord(*pos) for pos in pies_set}
    new_corners = {rotate_coord(*pos) for pos in corners}
    
    new_initial_ghosts = [rotate_coord(*pos) for pos in initial_ghosts]
    new_foods_list = [rotate_coord(*pos) for pos in foods_list]

    # 4. Cập nhật Foods Map mới (key là tọa độ)
    num_foods = len(foods_list)
    new_foods_list = [None] * num_foods
    new_foods_map = {}
    
    # Xoay từng tọa độ food theo thứ tự index cũ
    for old_pos, index in foods_map.items():
        new_pos = rotate_coord(*old_pos)
        
        # Đảm bảo new_foods_list giữ nguyên thứ tự bitmask (index)
        new_foods_list[index] = new_pos
        
        # Cập nhật foods_map mới
        new_foods_map[new_pos] = index
    return (new_grid, new_pacman_pos, new_pies_set, new_initial_ghosts,
            new_exit_pos, new_corners, new_foods_map, new_foods_list)
# --- KHỐI THỰC THI CHÍNH ĐỂ KIỂM TRA ---
if __name__ == '__main__':
    maps_folder = 'maps'
    map_file_name = 'task02_pacman_example_map.txt'
    map_file_path = os.path.join(maps_folder, map_file_name)

    try:
        # Tải dữ liệu ban đầu
        (grid, pacman_start, pies, ghosts, game_exit,
         corners, foods_map, foods_list) = load_map(map_file_path)
        ghost_paths = _calculate_ghost_paths(ghosts, grid)

        # --- Test 1: Teleport ---
        #print("\n--- TEST 1: DỊCH CHUYỂN GÓC (TELEPORT) ---")
        corner_pos = list(corners)[0]
        state_at_corner = State(pos=corner_pos, pie_time=0, foods_mask=0, total_steps=10)
        #print(f"Pacman đang ở góc {state_at_corner.pos}. Các bước đi hợp lệ:")
        teleport_moves = successors(state_at_corner, grid, pies, ghosts, ghost_paths, foods_map, corners)
        for move in teleport_moves:
            print(f"  - Hành động: {move[0]}")

        # --- Test 2: Map Rotation ---
        # print("\n--- TEST 2: XOAY BẢN ĐỒ ---")
        # print(f"Vị trí Pacman ban đầu: {pacman_start}")
        # print(f"Vị trí cổng thoát ban đầu: {game_exit}")

        # Giả lập hành động xoay bản đồ
        (rotated_grid, rotated_pacman, _, _, rotated_exit,
         _, _, _, _) = rotate_map_180(
            grid, pacman_start, foods_list, pies, ghosts, game_exit, corners
        )
        # print(f"Vị trí Pacman sau khi xoay: {rotated_pacman}")
        # print(f"Vị trí cổng thoát sau khi xoay: {rotated_exit}")

    except (FileNotFoundError, ValueError) as e:

        print(f"Lỗi: {e}")