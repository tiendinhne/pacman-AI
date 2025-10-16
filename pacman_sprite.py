import pygame
import os

class PacmanSprite:
    def __init__(self, assets_path='assets', tile_size=24):
        self.tile_size = tile_size
        self.frames = {}
        self.frame_index = 0
        self.direction = 'right'
        self.load_frames(assets_path)

    def load_frames(self, assets_path):
        directions = ['right', 'left', 'up', 'down']
        for dir in directions:
            path = os.path.join(assets_path, f'pacman-{dir}')
            images = []
            for filename in sorted(os.listdir(path)):
                img = pygame.image.load(os.path.join(path, filename)).convert_alpha()
                img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
                images.append(img)
            self.frames[dir] = images

    def update(self):
        self.frame_index = (self.frame_index + 1) % len(self.frames[self.direction])

    def draw(self, screen, pos):
        x, y = pos
        img = self.frames[self.direction][self.frame_index]
        screen.blit(img, (y * self.tile_size, x * self.tile_size))
