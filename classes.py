import sys

import pygame
from main_page import load_image


class Creature(pygame.sprite.Sprite):
    def __init__(self, type, pic_name, pos, *group):
        super().__init__(*group)
        self.image = load_image(pic_name, -1)
        self.pic_name = pic_name
        self.health = type
        self.speed = 2
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.animation = []
        self.is_alive = True
        # Параметры здоровья, скорости, положения, картинка и проверка на то, что существо живо.
        # Creature будет наследником pygame.sprite.Sprite, чтобы было удобнее передвигаться и ставить картинки

        self.frame = 0  # текущий кадр
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 80  # как быстро кадры меняются

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

    def update(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            if self.do_animation('up'):
                self.move('up')
        if key[pygame.K_s]:
            if self.do_animation('down'):
                self.move('down')
        if key[pygame.K_d]:
            if self.do_animation('right'):
                self.move('right')
        if key[pygame.K_a]:
            if self.do_animation('left'):
                self.move('left')

    def do_animation(self, direction):
        now = pygame.time.get_ticks()
        directory = self.pic_name.split("/")[0]
        if direction == 'left':
            self.animation = [pygame.transform.flip(load_image(f'{directory}/go_right/img_{i}.png'), True, False)
                              for i in range(1, 5)]
        else:
            self.animation = [load_image(f'{directory}/go_{direction}/img_{i}.png') for i in range(1, 5)]
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.animation):
                self.frame = 0
            self.image = self.animation[self.frame]
            return True
        return

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


class Enemy(Creature):

    def get_path(self):
        pass
        # Здесь волновым алгоритмом определяем, как легче пройти к игроку и разворачиваемся в ту сторону
        # и записываем в переменную direction. 'up', 'down', 'left', 'right' - наброски, их можно менять

    def check_can_attack(self, pos_enemy, pos_hero):
        x_hero, y_hero = self.get_coords(pos_hero)
        x_enemy, y_enemy = self.get_coords(pos_enemy)
        return x_enemy == x_hero or y_enemy == y_hero
        # Сюда нужно ещедобавить проверку на впередистоящие стены

    def do_attack(self):
        pass
    # Атака


class Player(Creature):
    def __init__(self, type, pic_name, pos, *group, ):
        super().__init__(type, pic_name, pos, *group)
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
        pass

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

    def interaction(self):
        pass
    # взаимодействие


# self.attacking_weapons.append(Weapon(flying=True, type=self.current_weapon, direction=self.direction))


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
        # Параметр type - тип оружия, flying - летит ли оружие(летит - когда кинул игрок,
        # не летит - когда лежит на земле),
        # visible - то же самое, что и is_alive у Creature, cells_to_fly - кол-во клеток,
        # которое ещё может пролететь оружие

    def do_fly(self, direction):
        pass

    def check_hit_enemy(self):
        pass

    def check_hit_wall(self):
        pass


if __name__ == '__main__':
    pygame.init()
    WINDOW_SIZE = (967, 560)
    screen = pygame.display.set_mode(WINDOW_SIZE)

    all_sprites = pygame.sprite.Group()
    creature = Player(30, 'ninja_player/ninja_player.png', (900, 510), all_sprites)

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        all_sprites.update()
        creature.update()

        screen.fill([20, 108, 121])
        all_sprites.draw(screen)
        pygame.display.flip()

        clock.tick(60)
