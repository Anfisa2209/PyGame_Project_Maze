import os
import sys

import pygame


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def create_list_wall():
    f = open('wall.csv', 'r')
    copy_f = f.readlines()
    f.close()
    if copy_f:
        for_a_while = []
        walls = []
        for i in copy_f:
            for j in i.strip('[]\n').split(', '):
                for_a_while.append(int(j))
            walls.append([(for_a_while[0], for_a_while[1]), (for_a_while[2], for_a_while[3])])
            for_a_while = []
        return walls
    # Создания списка всех стен (координаты начала и конца)


def check_conflict_with_wall(pos, direction=''):
    x, y = pos
    walls = create_list_wall()

    f = open('for_get_coords.csv', 'r')
    copy_f = f.readlines()
    width = int(copy_f[-1])
    f.close()

    lst_coords = [(x, y), (x + 10, y + 27), (x + 25, y), (x + 10, y), (x + 25, y + 10), (x, y + 13), (x + 25, y + 27),
                  (x + 15, y + 27), (x, y + 27)]
    for i in walls:
        start_x, start_y = i[0]
        end_x, end_y = i[1]
        for j, k in lst_coords:
            if start_y == end_y and start_y in range(y, y + 27) and j in range(min(start_x, end_x),
                                                                               max(start_x, end_x) + 1):
                if direction not in ['right', 'left'] or y not in range(start_y, start_y + width):
                    return True
            elif start_x == end_x and start_x in range(x - 1, x + 25) and k in range(min(start_y, end_y),
                                                                                     max(start_y, end_y) + 1):
                return True
    return False
    # Проверка столкновения со стеной


FPS = 80


class Creature(pygame.sprite.Sprite):
    def __init__(self, type, pic_name, pos, *group):
        super().__init__(*group)
        self.image = load_image(pic_name, -1)
        SPRITE_WIDTH, SPRITE_HEIGHT = 30, self.image.get_height()
        self.pic_name = pic_name
        self.health = type
        self.speed = 2
        self.is_alive = True

        self.rect = self.image.get_rect()
        self.pos = self.rect.x, self.rect.y = pos
        walk_up = load_image(pic_name.replace('_walk_right', '_walk_up'), -1)
        walk_down = load_image(pic_name.replace('_walk_right', "_walk_down"), -1)

        self.walk_right = [self.image.subsurface((i * SPRITE_WIDTH, 0, SPRITE_WIDTH, SPRITE_HEIGHT)) for i in range(2)]
        self.walk_left = [pygame.transform.flip(i, True, False) for i in self.walk_right]
        self.walk_up = [walk_up.subsurface((i * SPRITE_WIDTH, 0, SPRITE_WIDTH, walk_up.height)) for i in range(2)]
        self.walk_down = [walk_down.subsurface((i * SPRITE_WIDTH, 0, SPRITE_WIDTH, walk_down.height)) for i in range(2)]
        self.animation = self.walk_left
        # Параметры здоровья, скорости, положения, картинка и проверка на то, что существо живо.
        self.current_frame = 0
        self.frame_rate = 10  # Скорость смены кадров
        self.animation_timer = 0
        self.moving = False

        f = open('for_get_coords.csv', 'r')
        copy_f = f.readlines()
        self.column = len(copy_f) - 1
        self.row = copy_f[0].count('0')
        self.board = [[0 for _ in range(self.row)] for _ in range(self.column)]
        self.width = int(copy_f[-1])
        f.close()

        self.enemy_way = []

    def update_animation(self):
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.frame_rate:
                self.current_frame = (self.current_frame + 1) % len(self.animation)
                self.animation_timer = 0

    def draw(self, screen):
        screen.blit(self.animation[self.current_frame], self.pos)

    def do_die(self):
        self.is_alive = False

    # В этой функции существо умирает и удаляестя с поля(опционально - анимация смерти)

    def get_hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.do_die()
        # Получение урона, если хп меньше либо равно нулю, то смерть

    def move(self, direction):
        if direction == 'up':
            if not check_conflict_with_wall((self.rect.x, self.rect.y - self.speed)):
                self.rect.y -= self.speed
                self.animation = self.walk_up
        elif direction == 'down':
            if not check_conflict_with_wall((self.rect.x, self.rect.y + self.speed)):
                self.rect.y += self.speed
                self.animation = self.walk_down
        if direction == 'left':
            if not check_conflict_with_wall((self.rect.x - self.speed, self.rect.y), direction):
                self.rect.x -= self.speed
                self.animation = self.walk_left
        elif direction == 'right':
            if not check_conflict_with_wall((self.rect.x + self.speed, self.rect.y), direction):
                self.animation = self.walk_right
                self.rect.x += self.speed
        self.pos = (self.rect.x, self.rect.y)

    # Собственно, движение

    def get_coords(self, pos_event):
        left, top = 0, 0  # Отступы если вдруг основное поле не будет вплотную прилегать к окну
        if (pos_event[0] in range(left, self.width * len(self.board[0]) + left) and pos_event[1]
                in range(top, self.width * len(self.board) + top)):
            return (pos_event[0] - left) // self.width, (pos_event[1] - left) // self.width
        # Получение координат клетки на котором находится существо, pos которого мы получили

    def is_free(self, start_cell, finish_cell):
        walls = create_list_wall()
        x_start, y_start = [i * self.width for i in start_cell]
        x_finish, y_finish = [i * self.width for i in finish_cell]
        result = False
        if x_finish == x_start:
            result = check_conflict_with_wall((x_finish + 3, max(y_finish, y_start)))
        elif y_start == y_finish:
            result = check_conflict_with_wall((max(x_finish, x_start), y_start + 3))
        return True if not result else False

    # Проверяет есть ли между клетками стены


ENEMY_EVENT_TYPE = 30


class Enemy(Creature):

    def get_path(self, start, finish):
        INF = 99999
        x, y = start
        distance = [[INF] * self.row for _ in range(self.column)]
        try:
            distance[y][x] = 0
        except IndexError:
            print(x, y, 'IndexError')
        prev = [[None] * self.row for _ in range(self.column)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.row and 0 < next_y < self.column:
                    if self.is_free((x, y), (next_x, next_y)) and distance[next_y][next_x] == INF:
                        distance[next_y][next_x] = distance[y][x] + 1
                        prev[next_y][next_x] = (x, y)
                        queue.append((next_x, next_y))
        x, y = finish
        if distance[y][x] == INF or start == finish:
            return start  # Идти никуда не надо, либо невозможно либо уже дошли
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y
        # Здесь волновым алгоритмом определяем, как легче пройти к игроку и разворачиваемся в ту сторону и записываем в
        # переменную direction. 'up', 'down', 'left', 'right' - наброски, их можно менять

    def update(self, screen):
        screen.blit(self.animation[self.current_frame], self.pos)

    def move_enemy(self, pos_enemy, pos_hero):
        next_x, next_y = self.get_path(pos_enemy, pos_hero)
        if self.pos[0] < next_x:
            self.animation = self.walk_right
            self.rect.x += self.width
        if self.pos[0] > next_x:
            self.rect.x -= self.width
            self.animation = self.walk_left
        if self.pos[1] < next_y:
            self.rect.y += self.width
            self.animation = self.walk_down
        if self.pos[1] > next_y:
            self.rect.y -= self.width
            self.animation = self.walk_up
        self.pos = (self.rect.x, self.rect.y)

    def set_position(self, next_pos):
        pass

    # Меняет координаты врага

    def check_can_attack(self, pos_enemy, pos_hero):
        f = open('for_get_coords.csv', 'r')
        width = int(f.readlines()[-1])
        x_hero, y_hero = self.get_coords(pos_hero)
        x_enemy, y_enemy = self.get_coords(pos_enemy)
        result = []
        if x_enemy == x_hero:
            for i in range(min(y_enemy, y_hero), max(y_enemy, y_hero)):
                res = check_conflict_with_wall((x_enemy * width + 1, i * width + width))
                if res:
                    result.append(res)
        elif y_enemy == y_hero:
            for i in range(min(x_enemy, x_hero), max(x_enemy, x_hero)):
                res = check_conflict_with_wall((i * width + width, y_enemy * width + 1))
                if res:
                    result.append(res)
        return True if not result else False
        # Проверка на возможность атаки (если враг и игрок стоят в одном ряду или колонне и между ними нет стен)
        # если список пустой атака возможна

    def do_attack(self):
        pass
    # Атака


class Player(Creature):
    def __init__(self, type=0, pic_name='', pos=(), *group):
        super().__init__(type, pic_name, pos, *group)
        self.image = load_image(pic_name, -1)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.is_alive = True
        self.health = 3
        self.speed = 2
        self.first_weapons = 0
        self.second_weapons = 0
        self.third_weapons = 0
        self.current_weapon = 1
        self.direction = 1
        self.attacking_weapons = []

    def set_current(self, type):
        self.current_weapon = type

    # Меняем оружие

    def do_attack(self):
        self.attacking_weapons.append(Weapon(flying=True, type=self.current_weapon, direction=self.direction))

    # Атака
    def update(self):
        self.moving = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.move('left')
            self.animation = self.walk_left
            self.moving = True
        elif keys[pygame.K_d]:
            self.move('right')
            self.animation = self.walk_right
            self.moving = True
        elif keys[pygame.K_w]:
            self.move('up')
            self.animation = self.walk_up
            self.moving = True
        elif keys[pygame.K_s]:
            self.move('down')
            self.animation = self.walk_down
            self.moving = True
        else:

            self.current_frame = 0  # Если персонаж не двигается, остановить анимацию

    def take_weapon(self):
        # Берём оружие
        pass

    def take_cherry(self):
        # берём вишенку
        if self.health < 10:
            self.health += 1
        else:
            pass

    def jump(self):
        pass

    # Прыжок


class Cherry(pygame.sprite.Sprite):
    def __init__(self, image, pos, *group):
        super().__init__(*group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.pos = pos

    def draw(self, screen):
        screen.blit(self.image, self.pos)

    def update(self, player):
        if player.get_coords(player.pos) == player.get_coords(self.pos):
            pygame.mixer.music.load('data/music/cherry.mp3')
            pygame.mixer.music.play()
            self.pos = (1000, 3000)
            self.rect.x, self.rect.y = self.pos


class Weapon(pygame.sprite.Sprite):
    def __init__(self, type, pic_name, pos, direction='right', flying=False, *group):
        super().__init__(*group)
        self.image = load_image(pic_name)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.type = type
        self.damage = type
        self.range = type
        self.direction = direction
        self.flying = flying
        self.visible = True
        self.cells_to_fly = type
        # Параметр type - тип оружия, flying - летит ли оружие(летит - когда кинул игрок, не летит - когда лежит на
        # земле), visible - то же самое, что и is_alive у Creature, cells_to_fly - кол-во клеток, которое ещё может
        # пролететь оружие

    def get_taken(self):
        self.visible = False

    def do_fly(self, direction):
        pass

    def check_hit_enemy(self):
        pass

    def check_hit_wall(self):
        pass
    # Пока не удаляю, но эта функция не нужна ее заменяет check_conflict_whith_wall


class Spikes(pygame.sprite.Sprite):
    def __init__(self, pos, cell_size, *group):
        super().__init__(pos, cell_size, *group)
        self.image = load_image('spikes', -1)
        self.rect = pygame.rect.Rect(pos[0], pos[1], cell_size, cell_size)
        self.is_activated = False

    def do_activate(self):
        self.rect = self.image.get_rect()
        self.is_activated = True
        pass
    # Тут должна быть анимация открытия - закрытия, всё длиной в одну секунду. В каждый кадр рект должен быть, как у картинки. По окончании анимации self.is_activated = False, a self.rect = pygame.rect.Rect(pos[0], pos[1], cell_size, cell_size).
