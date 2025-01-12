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


def check_conflict_with_wall(pos):
    x, y = pos
    walls = create_list_wall()
    result = []
    for i in walls:
        start_x, start_y = i[0]
        end_x, end_y = i[1]
        if y == start_y == end_y and x in range(min(start_x, end_x), max(start_x, end_x) + 1):
            result.append(i)
        if x == start_x == end_x and y in range(min(start_y, end_y), max(start_y, end_y) + 1):
            result.append(i)
    return True if result else False
    # Проверка столкновения со стеной


class Creature(pygame.sprite.Sprite):

    def __init__(self, type, *group, pic_name, pos):
        super().__init__(type, *group, pic_name, pos)
        self.image = load_image(pic_name)
        self.health = type
        self.speed = 2
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.is_alive = True
        # Параметры здоровья, скорости, положения, картинка и проверка на то, что существо живо. Creature будет
        # наследником pygame.sprite.Sprite, чтобы было удобнее передвигаться и ставить картинки

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
            self.rect.y -= self.speed
        elif direction == 'down':
            self.rect.y += self.speed
        if direction == 'left':
            self.rect.x -= self.speed
        elif direction == 'right':
            self.rect.x += self.speed

    # Собственно, движение

    def get_coords(self, pos_event):
        f = open('for_get_coords.csv', 'r')
        copy_f = f.readlines()
        column = len(copy_f) - 1
        row = copy_f[0].count('0')
        board = [[0 for i in range(row)] for j in range(column)]
        width = int(copy_f[-1])
        left, top = 0, 0  # Отступы если вдруг основное поле не будет вплотную прилегать к окну
        if (pos_event[0] in range(left, width * len(board[0]) + left) and pos_event[1]
                in range(top, width * len(board) + top)):
            return (pos_event[0] - left) // width, (pos_event[1] - left) // width
        # Получение координат клетки на котором находится существо, pos которого мы получили


class Enemy(Creature):

    def get_path(self):
        pass
        # Здесь волновым алгоритмом определяем, как легче пройти к игроку и разворачиваемся в ту сторону и записываем в
        # переменную direction. 'up', 'down', 'left', 'right' - наброски, их можно менять

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
    def __init__(self, *group, pic_name, pos):
        super().__init__(*group, pic_name, pos)
        self.image = load_image(pic_name)
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

    def take_weapon(self):
        pass

    # Берём оружие

    def take_cherry(self):
        if self.health < 10:
            self.health += 1
        else:
            pass

    # берём вишенку

    def jump(self):
        pass

    #Прыжок


class Cherry(pygame.sprite.Sprite):
    def __init__(self, *group, pos):
        super().__init__(*group, pos)
        self.is_visible = True

    def get_taken(self):
        self.is_visible = 0


class Weapon(pygame.sprite.Sprite):
    def __init__(self, type, *group, pic_name, pos, direction='right', flying=False):
        super().__init__(type, *group, pic_name, pos, direction, flying)
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
