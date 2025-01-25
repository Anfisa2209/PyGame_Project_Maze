import pymorphy3

import classes
from random import randrange
import pygame

import main_page
from generate_maze import MazeGenerator

WINDOW_SIZE = WIDTH, HEIGHT = (950, 600)
pygame.init()
clock = pygame.time.Clock()
fps = 80
screen = pygame.display.set_mode(WINDOW_SIZE)


def start_game(window_size, cell_size, difficulty, player_pic_name):
    pygame.display.set_caption('Играть')
    paused = False
    if difficulty == 3:
        # 35
        window_size = 910, 595
    elif difficulty == 2:
        # 40 cell size
        window_size = 920, 600
    generator = MazeGenerator(window_size, cell_size)
    generator.main_loop()
    if generator.is_full:
        pygame.image.save(screen, 'data/maze.png')
        maze_fon = classes.load_image('maze.png')
        screen.blit(maze_fon, (0, 0))
        in_game = True
        time = 0
        spikes = []

        spikes_group = pygame.sprite.Group()
        cherries_group = pygame.sprite.Group()
        player_group = pygame.sprite.Group()

        cherry_image = pygame.transform.scale(classes.load_image('cherry.png', -1), (cell_size, cell_size))
        cherries = [classes.Cherry(cherry_image,
                                   (randrange(0, window_size[0], cell_size), randrange(0, window_size[1], cell_size)),
                                   cherries_group) for _ in range(10 * difficulty)]

        player = classes.Player(player_pic_name, (window_size[0] - cell_size, window_size[1] - cell_size),
                                *player_group)
        for _ in range(difficulty * 10):
            pos, direction = classes.choose_pos_for_spike()
            if pos == player.pos or player.get_coords(pos) == (0, 0):
                pos, direction = classes.choose_pos_for_spike()
            spike = classes.Spikes(pos, cell_size, direction, spikes_group)
            spikes.append(spike)

        while in_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    in_game = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                        if paused:
                            pygame.image.save(screen, 'data/paused_maze.png')
                    if event.key == pygame.K_e:
                        if player.cherry_list:
                            player.health += 1
                            player.cherry_list.pop(-1)
            if not paused:
                screen.blit(maze_fon, (0, 0))
                for spike in spikes:
                    spike.draw(screen)
                    if player.get_coords(player.pos) != player.get_coords(spike.pos):
                        spike.is_activated = False
                        spike.current_frame = 0
                    spike.update_animation()
                for cherry in cherries:
                    cherry.draw(screen)
                    if player.take_cherry(cherry):
                        play_music('cherry.mp3', False)
                if pygame.sprite.spritecollide(player, spikes_group, False):
                    for spike in pygame.sprite.spritecollide(player, spikes_group, False):
                        if player.get_coords(player.pos) == player.get_coords(spike.pos):
                            spike.do_activate()
                            if spike.time >= 30:
                                player.get_hit(1)
                                spike.time = 0
                                play_music('spike_beat.mp3', False)

                player.update()
                player.update_animation()
                player.draw(screen)
                write_text(str(player.health), cell_size // 3, cell_size // 3, 40, (209, 96, 88))
                if player.health == 0 or not player.is_alive:
                    in_game = False
                    game_ended('Вы проиграли!', window_size, cell_size, difficulty, player_pic_name,
                               player.picked_cherries, time, player.health)
                if player.get_coords(player.pos) == (0, 0) and in_game:
                    game_ended('Вы выиграли!', window_size, cell_size, difficulty, player_pic_name,
                               player.picked_cherries, time, player.health)
                clock.tick(fps)
                pygame.display.flip()
            else:
                paused_maze_fon = classes.load_image('paused_maze.png')
                screen.blit(paused_maze_fon, (0, 0))


def play_music(name, long):
    # проигрывает мелодию
    if long:
        pygame.mixer.init()
        song = pygame.mixer.Sound('data/music/' + name)
        return song
    else:
        # проигрывает звук
        pygame.mixer.music.load('data/music/' + name)
        pygame.mixer.music.play()


def game_ended(text, window_size, cell_size, difficulty, player_pic_name, cherry, time, health):
    pygame.display.set_caption(text)
    play_music('lose.mp3' if text == 'Вы проиграли!' else 'win.mp3', False)

    button_image = pygame.transform.scale(classes.load_image('buttons/button.png', -1), (150, 50))
    rect = (WIDTH // 4, 15, 500, 500)
    play_again = main_page.Button(button_image, rect[0] * 1.5 + 150, rect[1] + 400, 'играть снова', 'Играть снова')
    go_back = main_page.Button(button_image, rect[0] * 1.5 + 150, rect[1] + 325, 'Играть', 'На главную')
    cherry_word = pymorphy3.MorphAnalyzer().parse(change_word_form("вишенка", cherry))[0].inflect({"accs", "sing"})[0]
    lines = [f'Вы собрали {cherry} {cherry_word}',
             f'У вас осталось {health} {change_word_form("жизнь", health)}',
             f'Вы потратили {time} {change_word_form("минута", time)}']

    font = pygame.font.Font(None, 50)
    text_color = (199, 62, 64) if text == 'Вы проиграли!' else (242, 162, 58)
    text = font.render(text, True, text_color)
    text_x, text_y = rect[0] + 130, rect[1] + 50

    color = 55, 102, 53
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (31, 71, 49), rect, width=5)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                go_back.on_click(pygame.mouse.get_pos())
                if play_again.check_mouse_pos(pygame.mouse.get_pos()):
                    start_game(window_size, cell_size, difficulty, player_pic_name)
        screen.blit(classes.load_image('maze.png'), (0, 0))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (31, 71, 49), rect, width=5)  # темная обводка
        screen.blit(text, (text_x, text_y))
        for i in range(1, len(lines) + 1):
            write_text(lines[i - 1], text_x - 30, text_y + 35 * i, 35, text_color)
        play_again.update()
        go_back.update()
        pygame.display.update()


def write_text(text, x, y, size, text_color):
    font = pygame.font.Font(None, size)
    text = font.render(text, True, text_color)
    screen.blit(text, (x, y))


def change_word_form(word, number):
    morph = pymorphy3.MorphAnalyzer()
    word = morph.parse(word)[0]
    word = word.make_agree_with_number(number)[0]
    return word


if __name__ == '__main__':
    start_game((960, 600), 60, 1, 'players/black_player/black_player_walk_right.png')
    # Называем по принципу - monsters/monster2/monster2_walk_right.png
    # простой - 60, средний - 40, сложный - 35
