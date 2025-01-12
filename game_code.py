import classes
import random
import pygame

from generate_maze import MazeGenerator

def start_game(window_size, cell_size, difficulty):
    generator = MazeGenerator(window_size, cell_size)
    generator.main_loop()
    if generator.is_full:
        WAVE = pygame.USEREVENT + 1
        pygame.time.set_timer(WAVE, 10)
        in_game = True
        monsters = []
        cherries = []
        weapons = []
        monster_group = pygame.sprite.Group
        cherries_group = pygame.sprite.Group
        weapons_group = pygame.sprite.Group
        for i in range (3 * difficulty):
            enemy_type = random.randint(10)
            if enemy_type <= 7:
                type = 1
            elif enemy_type <= 9:
                type = 2
            else:
                type = 3
            enemy = classes.Enemy(type, monster_group, monster_pic_name, (random.randint(window_size[0]//cell_size) * cell_size, random.randint(window_size[1]//cell_size) * cell_size))
            monsters.append(enemy)
        player = classes.Player(player_pic_name, (((window_size[0]//cell_size) - 1) * cell_size, ((window_size[1]//cell_size) - 1) * cell_size))
        for i in range(difficulty * 3):
            cherry = classes.Cherry(cherries, (random.randint(window_size[0]//cell_size) * cell_size, random.randint(window_size[1]//cell_size) * cell_size))
            cherries.append(cherry)
        for i in range(difficulty * 10):
            weapon_type = random.randint(10)
            if enemy_type <= 5:
                type = 1
            elif enemy_type <= 8:
                type = 2
            else:
                type = 3
            weapon = classes.Weapon(type, weapons_group, weapon_pic_name, (random.randint(window_size[0]//cell_size) * cell_size, random.randint(window_size[1]//cell_size) * cell_size))
            weapons.append(weapon)
            #monster_pic_name, player_pic_name и weapon_pic_name - названия картинк игрока, монстра и оружия
            while in_game:
                for monster in monsters:
                    monster_pos = monster.get_coords()
                    player_pos = player.get_coords()
                    if monster.check_can_attack(monster_pos, player_pos):
                        monster.do_attack()
                    else:
                        monster.get_path()
                        monster.move(direction)
                        #переменную direction я ещё не знаю, как получаем, пока так, потом изменю
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w:
                            player.rect.y += player.speed
                        elif event.key == pygame.K_s:
                            player.rect.y -= player.speed
                        elif event.key == pygame.K_a:
                            player.rect.x += player.speed
                        elif event.key == pygame.K_d:
                            player.rect.x -= player.speed
                        elif event.key == pygame.K_e:
                            if pygame.sprite.spritecollide(player, cherries_group, False)[0] in cherries_group:
                                cherry.get_taken()
                                cherries_group.remove(cherry)
                                cherries.remove(cherry)
                            elif pygame.sprite.spritecollide(player, weapons_group, False)[0] in weapons_group:
                                weapon.get_taken()
                                weapons_group.remove(weapon)
                                weapon.remove(weapon)
                        elif event.key == pygame.K_SPACE:
                            pass
                            #Тут пауза
                    elif event.type == WAVE:
                        for i in range(3 * difficulty):
                            enemy_type = random.randint(10)
                            if enemy_type <= 7:
                                type = 1
                            elif enemy_type <= 9:
                                type = 2
                            else:
                                type = 3
                            enemy = classes.Enemy(type, monster_group, monster_pic_name, (
                            random.randint(window_size[0] // cell_size) * cell_size,
                            random.randint(window_size[1] // cell_size) * cell_size))
                            monsters.append(enemy)
                        player = classes.Player(player_pic_name, (((window_size[0] // cell_size) - 1) * cell_size,
                                                                  ((window_size[1] // cell_size) - 1) * cell_size))
                        for i in range(difficulty * 3):
                            cherry = classes.Cherry(cherries, (random.randint(window_size[0] // cell_size) * cell_size,
                                                               random.randint(window_size[1] // cell_size) * cell_size))
                            cherries.append(cherry)
                        for i in range(difficulty * 10):
                            weapon_type = random.randint(10)
                            if enemy_type <= 5:
                                type = 1
                            elif enemy_type <= 8:
                                type = 2
                            else:
                                type = 3
                            weapon = classes.Weapon(type, weapons_group, weapon_pic_name, (
                            random.randint(window_size[0] // cell_size) * cell_size,
                            random.randint(window_size[1] // cell_size) * cell_size))
                            weapons.append(weapon)
                if player.health == 0:
                    in_game = False