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


class Creature(pygame.sprite.Sprite):

    def __init__(self, type, *group, pic_name, pos):
        super().__init__(type, *group, pic_name, pos)
        self.image = load_image(pic_name)
        self.health = type
        self.speed = 2
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.is_alive = True
        #Параметры здоровья, скорости, положения, картинка и проверка на то, что существо живо. Creature будет наследником pygame.sprite.Sprite, чтобы было удобнее передвигаться и ставить картинки


    def do_die(self):
        self.is_alive = False
    # В этой функции существо умирает и удаляестя с поля(опционально - анимация смерти)

    def get_hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.do_die()
        #Получение урона, если хп меньше либо равно нулю, то смерть

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


class Enemy(Creature):

    def get_path(self):
        pass
        # Здесь волновым алгоритмом определяем, как легче пройти к игроку и разворачиваемся в ту сторону и записываем в переменную direction. 'up', 'down', 'left', 'right' - наброски, их можно менять
    def check_can_attack(self):
        pass
        #Тут проверяем, можем ли атаковать
    def do_attack(self):
        pass
    #Атака

class Player(Creature):
    def __init__(self, type, *group, pic_name, pos):
        super().__init__(type, *group, pic_name, pos)
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
    #Меняем оружие

    def do_attack(self):
        self.attacking_weapons.append(Weapon(flying=True, type=self.current_weapon, direction=self.direction))
    #Атака

    def take_weapon(self):
        pass
    #Берём оружие

    def take_cherry(self):
        if self.health < 10:
            self.health += 1
        else:
            pass
    #берём вишенку
    def interaction(self):
        pass
    #взаимодействие

class Weapon(pygame.sprite.Sprite):
    def __init__(self, type, *group, pic_name, pos, direction, flying):
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
        #Параметр type - тип оружия, flying - летит ли оружие(летит - когда кинул игрок, не летит - когда лежит на земле), visible - то же самое, что и is_alive у Creature, cells_to_fly - кол-во клеток, которое ещё может пролететь оружие

    def do_fly(self, direction):
        pass

    def check_hit_enemy(self):
        pass

    def check_hit_wall(self):
        pass