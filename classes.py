import os
import random
import sys

import pygame

lst_spikes = []


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


def choose_pos_for_spike():
    walls = create_list_wall()
    result = walls[random.randint(0, len(walls) - 1)]
    if result not in lst_spikes:
        lst_spikes.append(result)
        xy = 'x' if result[0][0] == result[1][0] else 'y'
        print(result, xy)
        return result[0], xy
    return choose_pos_for_spike()


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


class Player:
    def __init__(self, pic_name, pos, *group):
        super().__init__(*group)
        self.image = load_image(pic_name, -1)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.pos = pos

        self.is_alive = True
        self.health = 5
        self.speed = 2
        self.is_alive = True
        self.picked_cherries = 0  # сколько вишенок собрал герой
        # Параметры здоровья, скорости, положения, картинка и проверка на то, что существо живо.

        SPRITE_WIDTH, SPRITE_HEIGHT = 30, self.image.get_height()  # размер спрайтов
        walk_up = load_image(pic_name.replace('_walk_right', '_walk_up'), -1)
        walk_down = load_image(pic_name.replace('_walk_right', "_walk_down"), -1)

        self.walk_right = [self.image.subsurface((i * SPRITE_WIDTH, 0, SPRITE_WIDTH, SPRITE_HEIGHT)) for i in range(2)]
        self.walk_left = [pygame.transform.flip(i, True, False) for i in self.walk_right]
        self.walk_up = [walk_up.subsurface((i * SPRITE_WIDTH, 0, SPRITE_WIDTH, walk_up.height)) for i in range(2)]
        self.walk_down = [walk_down.subsurface((i * SPRITE_WIDTH, 0, SPRITE_WIDTH, walk_down.height)) for i in range(2)]
        self.animation = self.walk_left  # анимация

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

    def update_animation(self):
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.frame_rate:
                self.current_frame = (self.current_frame + 1) % len(self.animation)
                self.animation_timer = 0

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

    def draw(self, screen):
        screen.blit(self.animation[self.current_frame], self.pos)

    def do_die(self):
        self.is_alive = False

    # В этой функции существо умирает и удаляестя с поля(опционально - анимация смерти)

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
    def get_hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.do_die()
        # Получение урона, если хп меньше либо равно нулю, то смерть

    def take_cherry(self, cherry):
        if self.get_coords(cherry.pos) == self.get_coords(self.pos):
            cherry.pos = (1000, 3000)
            cherry.rect.x, cherry.rect.y = cherry.pos
            self.picked_cherries += 1
            self.health += 1
            return True

    def get_coords(self, pos_event):
        left, top = 0, 0  # Отступы если вдруг основное поле не будет вплотную прилегать к окну
        if (pos_event[0] in range(left, self.width * len(self.board[0]) + left) and pos_event[1]
                in range(top, self.width * len(self.board) + top)):
            return (pos_event[0] - left) // self.width, (pos_event[1] - left) // self.width
        # Получение координат клетки на котором находится существо, pos которого мы получили

    def is_free(self, start_cell, finish_cell):
        x_start, y_start = [i * self.width for i in start_cell]
        x_finish, y_finish = [i * self.width for i in finish_cell]
        result = False
        if x_finish == x_start:
            result = check_conflict_with_wall((x_finish + 3, max(y_finish, y_start)))
        elif y_start == y_finish:
            result = check_conflict_with_wall((max(x_finish, x_start), y_start + 3))
        return True if not result else False


class Cherry(pygame.sprite.Sprite):
    def __init__(self, image, pos, *group):
        super().__init__(*group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.pos = pos

    def draw(self, screen):
        screen.blit(self.image, self.pos)


class Spikes(pygame.sprite.Sprite):
    def __init__(self, pos, cell_size, direction, *group):
        super().__init__(*group)
        self.image = load_image('spikes.png', -1)
        self.rect = pygame.rect.Rect(pos[0], pos[1], cell_size, cell_size)
        self.pos = pos

        self.direction = direction
        self.cell_size = cell_size
        SPRITE_WIDTH = SPRITE_HEIGHT = 13
        self.animation = [self.image.subsurface((i * SPRITE_WIDTH, 0, SPRITE_WIDTH, SPRITE_HEIGHT))
                          for i in range(2, 11)]
        self.current_frame = 0
        self.frame_rate = 10  # Скорость смены кадров
        self.animation_timer = 0
        self.is_activated = False

        self.time = 0

    def do_activate(self):
        self.is_activated = True
        self.time += 1

    def draw(self, screen):
        cur_image = pygame.transform.scale(self.animation[self.current_frame], (self.cell_size, self.cell_size))
        if self.direction == 'x':
            cur_image = pygame.transform.rotate(cur_image, 90)
        screen.blit(pygame.transform.flip(cur_image, False, False), self.pos)

    def update_animation(self):
        if self.is_activated:
            self.animation_timer += 1
            if self.animation_timer >= self.frame_rate:
                self.current_frame = (self.current_frame + 1) % len(self.animation)
                self.animation_timer = 0
        else:
            self.current_frame = 0

    # Тут должна быть анимация открытия - закрытия, всё длиной в одну секунду. В каждый кадр рект должен быть, как у
    # картинки. По окончании анимации self.is_activated = False, a self.rect = pygame.rect.Rect(pos[0], pos[1],
    # cell_size, cell_size).
