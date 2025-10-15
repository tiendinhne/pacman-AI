# game.py
import pygame
from map_loader import Maze
from pacman import Pacman
#from ghost import Ghost
from utils import load_assets, draw_grid

class Game:
    def __init__(self, map_path):
        pygame.init()
        self.maze = Maze(map_path)
        self.pacman = Pacman(self.maze.pacman_start)
        #self.ghosts = [Ghost(pos) for pos in self.maze.ghost_starts]
        self.assets = load_assets()
        self.tile_size = 24
        self.screen = pygame.display.set_mode(
            (self.maze.width * self.tile_size, self.maze.height * self.tile_size)
        )
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(10)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_DOWN]: dy = 1
        if keys[pygame.K_LEFT]: dx = -1
        if keys[pygame.K_RIGHT]: dx = 1
        self.pacman.move(dx, dy, self.maze)

    def render(self):
        self.screen.fill((0, 0, 0))
        draw_grid(self.screen, self.maze, self.assets, self.tile_size)
        pygame.display.flip()
