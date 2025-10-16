import pygame
import os
from pacman_sprite import PacmanSprite

TILE_SIZE = 24



class GameUI:
    def __init__(self, grid, width, height):
        pygame.init()
        self.grid = grid
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width * TILE_SIZE, height * TILE_SIZE + 40))
        pygame.display.set_caption("Pacman Arcade")
        self.font = pygame.font.SysFont('Courier New', 20)
        self.pacman_sprite = PacmanSprite()
        self.wall_img = pygame.image.load('assets/wall_blue.png')
        self.wall_img = pygame.transform.scale(self.wall_img, (TILE_SIZE, TILE_SIZE))
        self.ghost_imgs = {
            0: pygame.image.load('assets/ghosts/blinky.png'),
            1: pygame.image.load('assets/ghosts/pinky.png'),
            2: pygame.image.load('assets/ghosts/inky.png'),
            3: pygame.image.load('assets/ghosts/clyde.png')
        }
        for i in self.ghost_imgs:
            self.ghost_imgs[i] = pygame.transform.scale(self.ghost_imgs[i], (TILE_SIZE, TILE_SIZE))
        self.mode_button_rect = pygame.Rect(670, self.height * TILE_SIZE + 5, 180, 30)
    def draw_mode_button(self, game_mode):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.mode_button_rect.collidepoint(mouse_pos)

        bg_color = (70, 70, 70) if is_hovered else (50, 50, 50)
        border_color = (255, 255, 255) if is_hovered else (200, 200, 200)

        pygame.draw.rect(self.screen, bg_color, self.mode_button_rect)
        pygame.draw.rect(self.screen, border_color, self.mode_button_rect, 2)

        label = self.font.render(f"MODE: {game_mode.upper()}", True, (255, 255, 255))
        label_rect = label.get_rect(center=self.mode_button_rect.center)
        self.screen.blit(label, label_rect)

        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.mode_button_rect.collidepoint(mouse_pos)

        # Màu nền thay đổi khi hover
        bg_color = (70, 70, 70) if is_hovered else (50, 50, 50)
        border_color = (255, 255, 255) if is_hovered else (200, 200, 200)

        # Vẽ nút
        pygame.draw.rect(self.screen, bg_color, self.mode_button_rect)
        pygame.draw.rect(self.screen, border_color, self.mode_button_rect, 2)

        # Vẽ chữ
        label = self.font.render(f"MODE: {game_mode.upper()}", True, (255, 0, 0))
        label_rect = label.get_rect(center=self.mode_button_rect.center)
        self.screen.blit(label, label_rect)


    def draw_grid(self, pacman_pos, ghost_positions, foods, pies, exit_pos, pie_time, steps, corners, game_mode):
        self.screen.fill((0, 0, 0))

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == '%':
                    self.screen.blit(self.wall_img, (x*TILE_SIZE, y*TILE_SIZE))

        for fx, fy in foods:
            radius = 6 if (fx, fy) in corners else 3
            color = (255, 255, 0) if radius == 6 else (255, 255, 255)
            pygame.draw.circle(self.screen, color, (fy*TILE_SIZE+12, fx*TILE_SIZE+12), radius)

        for px, py in pies:
            pygame.draw.circle(self.screen, (0, 255, 255), (py*TILE_SIZE+12, px*TILE_SIZE+12), 6)

        ex, ey = exit_pos
        pygame.draw.rect(self.screen, (0, 255, 0), (ey*TILE_SIZE, ex*TILE_SIZE, TILE_SIZE, TILE_SIZE))

        for i, (gx, gy) in enumerate(ghost_positions):
            ghost_img = self.ghost_imgs[i % 4]
            self.screen.blit(ghost_img, (gy*TILE_SIZE, gx*TILE_SIZE))

        self.pacman_sprite.draw(self.screen, pacman_pos)
        self.pacman_sprite.update()

        score_text = self.font.render(f"SCORE: {steps}", True, (255, 255, 255))
        highscore_text = self.font.render(f"HIGHSCORE: ????? ", True, (255, 255, 255))
        pie_text = self.font.render(f"PIE: {pie_time} | FOODS LEFT: {len(foods)}", True, (255, 255, 255))

        self.screen.blit(score_text, (10, self.height * TILE_SIZE + 10 ))
        self.screen.blit(highscore_text, (200, self.height * TILE_SIZE + 10))
        self.screen.blit(pie_text, (400, self.height * TILE_SIZE + 10))
        # mode_text = self.font.render(f"MODE: {game_mode.upper()}", True, (255, 255, 255))
        # self.screen.blit(mode_text, (600, self.height * TILE_SIZE + 5))
        self.draw_mode_button(game_mode)

        pygame.display.flip()
