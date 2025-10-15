import os
from dataclasses import dataclass
from typing import Tuple, Set, List, FrozenSet

# Quy ước ký tự trên bản đồ
WALL = '%'
PACMAN = 'P'
FOOD = '.'
PIE = 'O'
GHOST = 'G'
EXIT = 'E'
EMPTY = ' '

@dataclass(frozen=True, order=True)
class State:
    """
    Định nghĩa State chi tiết cho bài toán tìm đường của Pacman.

    Attributes:
        y (int): Tọa độ hàng của Pacman.
        x (int): Tọa độ cột của Pacman.
        pie_time (int): Thời gian hiệu lực còn lại của Pie. 
                        Bằng 0 nếu Pacman không trong trạng thái ăn bánh.
        remaining_foods (FrozenSet[Tuple[int, int]]): Set các tọa độ thức ăn còn lại.
    """
    pos: Tuple[int, int]
    remaining_foods: FrozenSet[Tuple[int, int]]

def load_map(path: str) -> Tuple[List[str], Tuple[int, int], Set[Tuple[int, int]], Set[Tuple[int, int]], List[Tuple[int, int]], Tuple[int, int]]:
    """
    Đọc và phân tích file bản đồ .txt.

    Args:
        path (str): Đường dẫn đến file bản đồ.

    Returns:
        Một tuple chứa:
        - grid (List[str]): Bản đồ dưới dạng lưới 2D.
        - start_pos (Tuple[int, int]): Tọa độ (y, x) của Pacman.
        - foods_set (Set[Tuple[int, int]]): Set các tọa độ thức ăn.
        - pies_set (Set[Tuple[int, int]]): Set các tọa độ bánh.
        - ghosts_info (List[Tuple[int, int]]): List các tọa độ của ma.
        - exit_pos (Tuple[int, int]): Tọa độ (y, x) của cổng thoát.
    """
    grid = []
    start_pos = None
    foods_set = set()
    pies_set = set()
    ghosts_info = []
    exit_pos = None

    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy file bản đồ tại: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        for y, line in enumerate(f):
            # Loại bỏ ký tự xuống dòng ở cuối
            clean_line = line.rstrip('\n')
            grid.append(list(clean_line))
            for x, char in enumerate(clean_line):
                pos = (y, x)
                if char == PACMAN:
                    start_pos = pos
                elif char == FOOD:
                    foods_set.add(pos)
                elif char == PIE:
                    pies_set.add(pos)
                elif char == GHOST:
                    ghosts_info.append(pos)
                elif char == EXIT:
                    exit_pos = pos

    if start_pos is None:
        raise ValueError("Không tìm thấy vị trí bắt đầu của Pacman ('P') trong bản đồ.")

    return grid, start_pos, foods_set, pies_set, ghosts_info, exit_pos

# --- Phần kiểm tra ---
if __name__ == '__main__':
    # File map có tên 'task02_pacman_example_map.txt'
    # và vị trí của file là /maps/task02_pacman_example_map.txt
    maps_folder = 'maps'
    map_file_name = 'task02_pacman_example_map.txt'
    map_file_path = os.path.join(maps_folder, map_file_name)

    try:
        # Tải bản đồ
        grid, pacman_start, foods, pies, ghosts, game_exit = load_map(map_file_path)

        # In thông tin đã trích xuất
        print(f" Đã tải bản đồ thành công từ '{map_file_path}'")
        print("-" * 30)

        print(f"Grid dimensions: {len(grid)} rows x {len(grid[0])} cols")

        print(f"\n Vị trí Pacman (P): {pacman_start}")
        print(f" Vị trí cổng thoát (E): {game_exit}")

        print(f"\n Thức ăn ({len(foods)}): {sorted(list(foods))}")
        print(f" Bánh ({len(pies)}): {sorted(list(pies))}")
        print(f" Ma ({len(ghosts)}): {ghosts}")
        print("-" * 30)

        # Tạo một State ban đầu để minh họa
        initial_state = State(pos=pacman_start, remaining_foods=frozenset(foods))
        print(" Ví dụ về State ban đầu:")
        print(initial_state)

    except (FileNotFoundError, ValueError) as e:
        print(f"Lỗi: {e}")