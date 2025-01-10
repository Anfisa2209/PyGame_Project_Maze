import classes

from generate_maze import MazeGenerator

def start_game(window_size, cell_size):
    generator = MazeGenerator(window_size, cell_size)
    generator.main_loop()
