
# utils.py
import pygame

def load_assets():
    assets = {}
    try:
        assets["%"]= pygame.image.load('assets/wall.png')
        assets["P"]= pygame.image.load('assets/pacman.png')
        assets["."]= pygame.image.load('assets/food.png')
        assets["G"]= pygame.image.load('assets/blue_ghost.png')
        assets["E"]= pygame.image.load('assets/coint_path.png')
        assets["O"]= pygame.image.load('assets/apple.png')
        assets[" "]= pygame.Surface((24, 24))  # empty tile
    except Exception as e:
        print("Lỗi khi load ảnh:", e)
    return assets

def draw_grid(screen, maze, assets, tile_size):
    for y, row in enumerate(maze.grid):
        for x, cell in enumerate(row):
            sprite = assets.get(cell, assets[' '])
            screen.blit(sprite, (x * tile_size, y * tile_size))
