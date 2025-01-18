import classes
import random
import pygame

from generate_maze import MazeGenerator

WAVE = pygame.USEREVENT + 1


def start_game(window_size, cell_size, difficulty, player_pic_name):
    generator = MazeGenerator(window_size, cell_size)
    generator.main_loop()
    player = classes.Player(type=1, pic_name=player_pic_name,
                            pos=(((window_size[0] // cell_size) - 1) * cell_size,
                                 ((window_size[1] // cell_size) - 1) * cell_size))
    if generator.is_full:
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
        for _ in range(3 * difficulty):  # создание врагов
            enemy_type = random.randint(0, 10)
            if enemy_type <= 7:
                enemy_type = 1
            elif enemy_type <= 9:
                enemy_type = 2
            else:
                enemy_type = 3
            enemy = classes.Enemy(enemy_type, f'monsters/monster{enemy_type}/moster{enemy_type}_walk_right.png', (
                random.randint(0, window_size[0] // cell_size) * cell_size,
                random.randint(0, window_size[1] // cell_size) * cell_size), monster_group)
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
                        weapon = pygame.sprite.spritecollide(player, weapons_group, False)
                    elif weapon:
                        weapon.get_taken()
                        weapons_group.remove(weapon)
                        weapon.remove(weapon)
                    elif event.key == pygame.K_SPACE:
                        pass
                        # Тут пауза
                if event.type == WAVE:
                    for _ in range(3 * difficulty):
                        enemy_type = random.randint(0, 10)
                        if enemy_type <= 7:
                            enemy_type = 1
                        elif enemy_type <= 9:
                            enemy_type = 2
                        else:
                            enemy_type = 3
                        enemy = classes.Enemy(enemy_type, f'monsters/monster{enemy_type}/monster{enemy_type}',
                                              (random.randint(0, window_size[0] // cell_size) * cell_size,
                                               random.randint(0, window_size[1] // cell_size) * cell_size),
                                              monster_group)
                        monsters.append(enemy)
                    for _ in range(difficulty * 3):
                        cherry = classes.Cherry((random.randint(0, window_size[0] // cell_size) * cell_size,
                                                 random.randint(0, window_size[1] // cell_size) * cell_size),
                                                cherries_group)
                        cherries.append(cherry)
                    for _ in range(difficulty * 10):
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
            player.update()
            if player.health == 0:
                in_game = False


start_game((957, 600), 50, 1, 'players/ninja_player')
