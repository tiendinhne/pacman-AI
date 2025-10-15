# pacman.py
class Pacman:
    def __init__(self, position):
        self.x, self.y = position

    def move(self, dx, dy, maze):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < maze.width and 0 <= new_y < maze.height:
            if not maze.is_wall(new_x, new_y):
                self.x, self.y = new_x, new_y
