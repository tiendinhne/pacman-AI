import pygame
from map_loader import load_map, _calculate_ghost_paths, get_ghost_positions
from map_loader import State, successors, is_goal
from game import GameUI

game_over = False
MANUAL = 'manual'
AUTO = 'auto'
game_mode = MANUAL
end_message = None
end_time = None



map_path = 'maps/task02_pacman_example_map.txt'
pygame.mixer.init()
bg_sound= pygame.mixer.SoundType("assets/sounds/backgroud.mp3")
win_sound = pygame.mixer.Sound("assets/sounds/pacman_chomp.wav")
lose_sound = pygame.mixer.Sound("assets/sounds/pacman_death.wav")
grid, pacman_start, pies, ghosts, exit_pos, corners, foods_map, foods_list = load_map(map_path)
ghost_paths = _calculate_ghost_paths(ghosts, grid)
ghost_order = ghosts  # giữ thứ tự ban đầu
ui = GameUI(grid, len(grid[0]), len(grid))
# khoi tao state
initial_food_mask = (1 << len(foods_list)) - 1
current_state = State(pacman_start, 0, initial_food_mask, 0)

# Dùng set để cập nhật bánh đã ăn
remaining_pies = set(pies)

running = True
clock = pygame.time.Clock()

while running:

    # Xử lý sự kiện (luôn chạy để có thể thoát game)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if ui.mode_button_rect.collidepoint(event.pos):
                game_mode = AUTO if game_mode == MANUAL else MANUAL

    # Nếu game chưa kết thúc → xử lý input và cập nhật trạng thái
    if not game_over:
        keys = pygame.key.get_pressed()
        direction = None
        if keys[pygame.K_UP]: direction = 'UP'
        elif keys[pygame.K_DOWN]: direction = 'DOWN'
        elif keys[pygame.K_LEFT]: direction = 'LEFT'
        elif keys[pygame.K_RIGHT]: direction = 'RIGHT'

        moved = False
        if game_mode == MANUAL and direction:
            for action, new_state, cost in successors(
                current_state, grid, pies, ghosts, ghost_paths, foods_map, corners
            ):
                if action == direction:
                    previous_pie_time = current_state.pie_time
                    current_state = new_state
                    if current_state.pos in remaining_pies:
                        remaining_pies.remove(current_state.pos)
                    ui.pacman_sprite.direction = direction.lower()
                    moved = True
                    break

        # Nếu không di chuyển, vẫn tăng bước để ghost di chuyển
        if game_mode == MANUAL and not moved:
            current_state = State(
                current_state.pos,
                max(0, current_state.pie_time - 1),
                current_state.foods_mask,
                current_state.total_steps + 1
            )

        # Cập nhật vị trí ghost
        ghost_positions_raw = get_ghost_positions(current_state.total_steps, ghosts, ghost_paths)
        ghost_positions = list(ghost_positions_raw)

        # Kiểm tra thắng/thua
        if is_goal(current_state, exit_pos):
            end_message = "🎉 YOU WIN!"
            end_time = pygame.time.get_ticks()
            win_sound.play()
            game_over = True

        elif current_state.pie_time == 0 and current_state.pos in ghost_positions:
            end_message = "💀 GAME OVER"
            end_time = pygame.time.get_ticks()
            lose_sound.play()
            game_over = True

    # Nếu game đã kết thúc → giữ ghost đứng yên
    if game_over:
        ghost_positions = list(get_ghost_positions(current_state.total_steps, ghosts, ghost_paths))

    # Tính lại danh sách thức ăn
    remaining_foods = [
        food for i, food in enumerate(foods_list)
        if (current_state.foods_mask >> i) & 1
    ]

    # Vẽ UI
    ui.draw_grid(
        current_state.pos,
        ghost_positions,
        remaining_foods,
        remaining_pies,
        exit_pos,
        current_state.pie_time,
        current_state.total_steps,
        corners,
        game_mode
    )

    # Hiển thị thông báo kết thúc nếu có
    if end_message:
        elapsed = pygame.time.get_ticks() - end_time
        label = ui.font_big.render(end_message, True, (255, 255, 0))
        label_rect = label.get_rect(center=(ui.screen.get_width() // 2, ui.screen.get_height() // 2))
        ui.screen.blit(label, label_rect)
        pygame.display.flip()
        if elapsed >= 5000:
            running = False

    pygame.display.flip()
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