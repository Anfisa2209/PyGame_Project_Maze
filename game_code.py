import classes
from random import randrange
import pygame

import main_page
from generate_maze import MazeGenerator

WAVE = pygame.USEREVENT + 1
ENEMY_EVENT_TYPE = 30
WINDOW_SIZE = WIDTH, HEIGHT = (950, 600)
pygame.init()
clock = pygame.time.Clock()
fps = 80
screen = pygame.display.set_mode(WINDOW_SIZE)


def start_game(window_size, cell_size, difficulty, player_pic_name):
    pygame.display.set_caption('Играть')
    if difficulty == 3:
        # 35
        window_size = 910, 595
    elif difficulty == 2:
        # 40 cell size
        window_size = 920, 600
    generator = MazeGenerator(window_size, cell_size)
    generator.main_loop()
    delay = 100
    pygame.time.set_timer(ENEMY_EVENT_TYPE, delay)

    if generator.is_full:
        pygame.image.save(screen, 'data/maze.png')
        maze_fon = classes.load_image('maze.png')
        screen.blit(maze_fon, (0, 0))
        pygame.time.set_timer(WAVE, 10)
        in_game = True
        spikes = []
        weapons = []
        spikes_group = pygame.sprite.Group()
        cherries_group = pygame.sprite.Group()
        player_group = pygame.sprite.Group()
        cherry_image = pygame.transform.scale(classes.load_image('cherry.png', -1), (cell_size, cell_size))
        cherries = [classes.Cherry(cherry_image,
                                   (randrange(0, window_size[0], cell_size), randrange(0, window_size[1], cell_size)),
                                   cherries_group) for _ in range(5 * difficulty)]

        player = classes.Player(type=1, pic_name=player_pic_name,
                                pos=(window_size[0] - cell_size, window_size[1] - cell_size), *player_group)
        # for i in range(difficulty*50):
        #     pos, direction = classes.choose_pos_for_spike()
        #     spike = classes.Spikes(pos, cell_size, spikes_group, xy=direction)
        #     spikes.append(spike)

        while in_game:
            # monsters[0].get_path((0, 0), (10, 5))
            # for monster in monsters:
            #     monster_pos = monster.get_coords((monster.rect.x, monster.rect.y))
            #     player_pos = player.get_coords((player.rect.x, player.rect.y))
            #     if monster.check_can_attack(monster_pos, player_pos):
            #         monster.do_attack()
            #     else:
            #         monster.get_path()
            #         monster.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    in_game = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pass
                        # Тут пауза
                # if event.type == WAVE:
                #     for _ in range(3 * difficulty):
                #         enemy_type = random.randint(0, 10)
                #         if enemy_type <= 7:
                #             enemy_type = 1
                #         elif enemy_type <= 9:
                #             enemy_type = 2
                #         else:
                #             enemy_type = 3
                #         enemy = classes.Enemy(enemy_type,
                #                               f'monsters/monster{enemy_type}/monster{enemy_type}_walk_right.png',
                #                               (random.randint(0, window_size[0] // cell_size) * cell_size,
                #                                random.randint(0, window_size[1] // cell_size) * cell_size),
                #                               monster_group)
                #         monsters.append(enemy)
                #     for _ in range(difficulty * 3):
                #         cherry = classes.Cherry((random.randint(0, window_size[0] // cell_size) * cell_size,
                #                                  random.randint(0, window_size[1] // cell_size) * cell_size),
                #                                 cherries_group)
                #         cherries.append(cherry)
                #     for _ in range(difficulty * 10):
                #         weapon_type = random.randint(0, 10)
                #         if weapon_type <= 5:
                #             weapon_type = 1
                #         elif weapon_type <= 8:
                #             weapon_type = 2
                #         else:
                #             weapon_type = 3
                #         weapon = classes.Weapon(weapon_type, f'weapons/weapon{weapon_type}.png', (
                #             random.randint(0, window_size[0] // cell_size) * cell_size,
                #             random.randint(0, window_size[1] // cell_size) * cell_size), weapons_group)
                #         weapons.append(weapon)
                # if event.type == ENEMY_EVENT_TYPE:
                #     for monster in monsters:
                #         monster.move_enemy((0, 0), player.get_coords(player.pos))
            screen.blit(maze_fon, (0, 0))
            for cherry in cherries:
                cherry.update(player)
                cherry.draw(screen)
            if pygame.sprite.spritecollide(player, spikes_group, False):
                for spike in pygame.sprite.spritecollide(player, spikes_group, False):
                    if spike.is_activated:
                        player.get_hit(1)
                    else:
                        spike.do_activate
            player.update()
            player.update_animation()
            player.draw(screen)
            if player.health == 0:
                in_game = False
                game_ended('Вы проиграли!', window_size, cell_size, difficulty, player_pic_name)
            if player.get_coords(player.pos) == (0, 0) and in_game:
                game_ended('Вы выиграли!', window_size, cell_size, difficulty, player_pic_name)
            clock.tick(fps)
            pygame.display.flip()


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


def game_ended(text, window_size, cell_size, difficulty, player_pic_name):
    pygame.display.set_caption(text)
    button_image = pygame.transform.scale(classes.load_image('buttons/button.png', -1), (150, 50))
    rect = (WIDTH // 4, 15, 500, 500)
    play_again = main_page.Button(button_image, rect[0] * 1.5 + 150, rect[1] + 400, 'играть снова', 'Играть снова')
    go_back = main_page.Button(button_image, rect[0] * 1.5 + 150, rect[1] + 325, 'Играть', 'На главную')

    play_music('lose.mp3' if text == 'Вы проиграли!' else 'win.mp3', False)
    font = pygame.font.Font(None, 50)
    text_color = (199, 62, 64) if text == 'Вы проиграли!' else (242, 162, 58)

    text = font.render(text, True, text_color)
    screen.blit(classes.load_image('maze.png'), (0, 0))
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
        pygame.draw.rect(screen, (31, 71, 49), rect, width=5)
        screen.blit(text, (text_x, text_y))
        play_again.update()
        go_back.update()
        pygame.display.update()


start_game((960, 600), 40, 1, 'players/black_player/black_player_walk_right.png')
# Называем по принципу - monsters/monster2/monster2_walk_right.png
# простой - 60, средний - 40, сложный - 35
