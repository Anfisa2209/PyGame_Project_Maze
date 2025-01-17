import random
import pygame

BLUE = [20, 108, 121]
BLACK = [39, 47, 48]
GREEN = [0, 255, 0]
WHITE = [255, 255, 255]


class Wall:
    def __init__(self, start, end):
        self.line = [start, end]
        self.exists = True


class Cell:
    def __init__(self, i, j, w):
        self.w = w
        self.i, self.j = i, j
        self.x, self.y = x, y = j * w, i * w

        self.visited = False
        self.walls = {
            'top': Wall([x, y], [x + w, y]),
            'left': Wall([x, y], [x, y + w]),
            'right': Wall([x + w, y], [x + w, y + w]),
            'bottom': Wall([x, y + w], [x + w, y + w]),
        }

    def neighbours(self):
        i, j = self.i, self.j
        return [
            [i - 1, j],  # top
            [i, j + 1],  # right
            [i + 1, j],  # bottom
            [i, j - 1]  # left
        ]


class Grid:
    def __init__(self, size, scale):
        self.size = size
        self.scale = scale

        self.cols = int(size[0] / scale)
        self.rows = int(size[1] / scale)

        self.grid = self.build_grid()
        self.width = self.grid[0][0].w
        self.board = [[0 for i in range(len(self.grid[0]))] for j in range(len(self.grid))]

        f = open('for_get_coords.csv', 'w')
        for i in self.board:
            f.write(str(i))
            f.write('\n')
        f.write(str(self.width))
        f.close()

    def __getitem__(self, i):
        return self.grid[i]

    def __iter__(self):
        for i in range(self.rows):
            for j in range(self.cols):
                yield self[i][j]

    def is_valid_cell(self, i, j):
        return not any([
            i < 0,
            j < 0,
            i > self.rows - 1,
            j > self.cols - 1
        ])

    def get_cells(self, cells):
        for i, j in cells:
            if self.is_valid_cell(i, j):
                yield self.grid[i][j]

    def build_grid(self):
        grid = [
            [Cell(i, j, self.scale) for j in range(self.cols)]
            for i in range(self.rows)
        ]
        return grid


class MazeGenerator:
    pygame.init()
    pygame.display.set_caption('maze generator')

    def __init__(self, size=(400, 320), scale=50):
        self.size, self.scale = size, scale
        self.setup()
        self.screen = pygame.display.set_mode(list(map(sum, zip(size, [2, 2]))))
        self.is_full = False
        self.walls = []
        self.flag_wall_ready = True

    def setup(self):
        self.grid = Grid(self.size, self.scale)
        self.stack = []
        self.clock = pygame.time.Clock()

        self.curr_c = self.grid[0][0]
        self.curr_c.visited = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                from main_page import choose_level
                self.screen.fill((0, 0, 0))
                choose_level()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.setup()
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(event.pos)
            # Позже уберем, пока еще надо

    def remove_walls(self, a, b):
        order_x = {1: ('left', 'right'),
                   -1: ('right', 'left')}.get(a.j - b.j, None)
        order_y = {
            1: ('top', 'bottom'),
            -1: ('bottom', 'top')}.get(a.i - b.i, None)

        if order_x is not None:
            a.walls[order_x[0]].exists = False
            b.walls[order_x[1]].exists = False

        if order_y is not None:
            a.walls[order_y[0]].exists = False
            b.walls[order_y[1]].exists = False

    def draw_cells(self):
        for cell in self.grid:
            if cell.visited:
                rect = pygame.Rect(
                    cell.x, cell.y,
                    self.grid.scale, self.grid.scale
                )
                color = GREEN if cell == self.curr_c else BLUE
                pygame.draw.rect(self.screen, color, rect)

            for wall in cell.walls.values():
                if wall.exists:
                    self.walls.append(wall.line) if wall.line not in self.walls else False
                    pygame.draw.line(self.screen, WHITE, *wall.line, width=2)
                else:
                    self.walls.remove(wall.line) if wall.line in self.walls else False

    def update(self):
        neighbours = self.grid.get_cells(self.curr_c.neighbours())
        neighbours = [n for n in neighbours if n.visited == False]

        if len(neighbours) != 0:
            next_c = random.choice(neighbours)
            self.remove_walls(self.curr_c, next_c)
            self.stack.append(self.curr_c)

            self.curr_c = next_c
            self.curr_c.visited = True

        elif len(self.stack) != 0:
            self.curr_c = self.stack.pop(-1)

        if len(self.stack) == 0:
            self.is_full = True

    def draw(self):
        if not self.is_full:
            self.draw_cells()
            self.screen.fill(BLACK)
            font = pygame.font.Font(None, 200)
            text = font.render('Loading...', True, (255, 255, 255))
            self.screen.blit(text, (200, 200))
            self.update()
        else:
            self.screen.fill(BLACK)
            self.draw_cells()
            self.update()
            if self.flag_wall_ready:
                f = open('wall.csv', 'w')
                for i in self.walls:
                    f.write(str([k for j in i for k in j if str(k).isdigit()]))
                    f.write('\n')
                f.close()
                self.flag_wall_ready = False

    def main_loop(self):
        while not self.is_full:
            self.handle_events()
            self.draw()
            pygame.display.flip()
