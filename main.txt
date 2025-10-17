import pygame
from map_loader import load_map, _calculate_ghost_paths, get_ghost_positions
from game import GameUI

MANUAL = 'manual'
AUTO = 'auto'
game_mode = MANUAL

map_path = 'maps/task02_pacman_example_map.txt'
grid, pacman_start, pies, ghosts, exit_pos, corners, foods_map, foods_list = load_map(map_path)
ghost_paths = _calculate_ghost_paths(ghosts, grid)

ui = GameUI(grid, len(grid[0]), len(grid))
pacman_pos = pacman_start
steps = 0
pie_time = 0

# Dùng set để cập nhật bánh đã ăn
remaining_pies = set(pies)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ui.mode_button_rect.collidepoint(event.pos):
                game_mode = AUTO if game_mode == MANUAL else MANUAL
                #print(f"Chuyển sang chế độ: {game_mode}")


    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    direction = None
    if keys[pygame.K_UP]: dx, dy = -1, 0; direction = 'up'
    elif keys[pygame.K_DOWN]: dx, dy = 1, 0; direction = 'down'
    elif keys[pygame.K_LEFT]: dx, dy = 0, -1; direction = 'left'
    elif keys[pygame.K_RIGHT]: dx, dy = 0, 1; direction = 'right'

    new_pos = (pacman_pos[0] + dx, pacman_pos[1] + dy)
    if grid[new_pos[0]][new_pos[1]] != '%':
        pacman_pos = new_pos
        steps += 1

        # Ăn bánh nếu có
        if new_pos in remaining_pies:
            pie_time = 5
            remaining_pies.remove(new_pos)
        else:
            pie_time = max(0, pie_time - 1)

        if direction:
            ui.pacman_sprite.direction = direction

    ghost_positions = get_ghost_positions(steps, ghosts, ghost_paths)
    ui.draw_grid(pacman_pos, ghost_positions, foods_list, remaining_pies, exit_pos, pie_time, steps, corners, game_mode)
    clock.tick(10)

if game_mode == MANUAL:
    # Xử lý phím điều khiển
    keys = pygame.key.get_pressed()
    ...
else:
    print("a*")
    # Chế độ AUTO: gọi A* nếu chưa có planned_actions
    # if not planned_actions:
    #     start_state = State(...)
    #     path, stats = astar(start_state, is_goal, successors, heuristic)
    #     planned_actions = extract_actions(path)
    # else:
    #     # Thực hiện bước tiếp theo
    #     next_action = planned_actions.pop(0)
    #     pacman_pos = apply_action(pacman_pos, next_action)
    #     steps += 1

# nút chọn chế độ chơi auto/control