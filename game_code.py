import classes
import random
import pygame

from generate_maze import MazeGenerator

WAVE = pygame.USEREVENT + 1
ENEMY_EVENT_TYPE = 30


def start_game(window_size, cell_size, difficulty, player_pic_name):
    pygame.init()
    clock = pygame.time.Clock()
    fps = 80
    if difficulty == 3:
        # 35
        window_size = 910, 595
    elif difficulty == 2:
        # 40 cell size
        window_size = 920, 600
    screen = pygame.display.set_mode(window_size)
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
        monsters = []
        weapons = []
        monster_group = pygame.sprite.Group()
        cherries_group = pygame.sprite.Group()
        weapons_group = pygame.sprite.Group()
        cherries = [classes.Cherry((random.randint(0, window_size[0] // cell_size) * cell_size,
                                    random.randint(0, window_size[1] // cell_size) * cell_size), cherries_group)
                    for _ in range(3 * difficulty)]

        player = classes.Player(type=1, pic_name=player_pic_name,
                                pos=(window_size[0] - cell_size, window_size[1] - cell_size))
        for _ in range(3 * difficulty):  # создание врагов
            enemy_type = random.randint(0, 10)
            if enemy_type <= 7:
                enemy_type = 1
            elif enemy_type <= 9:
                enemy_type = 2
            else:
                enemy_type = 3
            enemy = classes.Enemy(enemy_type, f'monsters/monster{enemy_type}/monster{enemy_type}_walk_right.png',
                                  (0, 0), monster_group)
            monsters.append(enemy)
        for _ in range(difficulty * 10):  # создание оружия
            weapon_type = random.randint(0, 10)
            if weapon_type <= 5:
                weapon_type = 1
            elif weapon_type <= 8:
                weapon_type = 2
            else:
                weapon_type = 3
            weapon = classes.Weapon(weapon_type, f'weapons/weapon{weapon_type}.png', (
                random.randint(0, window_size[0] // cell_size) * cell_size,
                random.randint(0, window_size[1] // cell_size) * cell_size), weapons_group)
            weapons.append(weapon)

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
                    if event.key == pygame.K_e:
                        cherry = pygame.sprite.spritecollide(player, cherries_group, False)
                        if cherry:
                            cherry.get_taken()
                            cherries_group.remove(cherry)
                            cherries.remove(cherry)
                        # weapon = pygame.sprite.spritecollide(player, weapons_group, False)
                    # elif weapon:
                    #     weapon.get_taken()
                    #     weapons_group.remove(weapon)
                    #     weapon.remove(weapon)
                    elif event.key == pygame.K_SPACE:
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
            # monsters[0].update(screen)
            # monsters[0].move_enemy(monsters[0].pos, player.get_coords(player.pos))
            player.update()
            player.update_animation()
            player.draw(screen)
            if player.health == 0:
                in_game = False
            clock.tick(fps)
            pygame.display.flip()


start_game((950, 600), 50, 1, 'players/ninja_player/ninja_player_walk_right.png')
# Называем по принципу - monsters/monster2/monster2_walk_right.png
# простой - 50, средний - 40, сложный - 35