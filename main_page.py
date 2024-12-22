import os
import sys
from random import randint

import pygame
import pygame_gui
from generate_maze import MazeGenerator


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


pygame.init()
SIZE = (967, 560)
OPENED_MENU = False  # открыто ли сейчас окно меню
screen = pygame.display.set_mode(SIZE)
maze_image = load_image('maze_fon.jpg', (255, 255, 255))
MANAGER = pygame_gui.UIManager(SIZE)
CLOCK = pygame.time.Clock()
screen.blit(maze_image, (0, 0))


class Button:
    """Класс кнопки"""

    def __init__(self, image, x_pos, y_pos, name, text='', font_size=20, icon=''):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.name = name
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.icon = icon
        if self.text:
            font = pygame.font.SysFont("Calibri", font_size, bold=True)
            self.text = font.render(self.text, True, "#408080")
            self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        if self.icon:
            icon_size = (30, 30)
            self.icon_image = pygame.transform.scale(load_image(self.icon), icon_size)
            self.icon_x, self.icon_y = image.get_size()
            self.icon_pos = (self.x_pos - icon_size[0] // 2, self.y_pos - icon_size[1] // 2)

    def update(self):
        screen.blit(self.image, self.rect)
        if self.text:
            screen.blit(self.text, self.text_rect)
        if self.icon:
            screen.blit(self.icon_image, self.icon_pos)

    def on_click(self, mouse_pos):
        """если нажали на кнопку"""
        global OPENED_MENU
        if self.check_mouse_pos(mouse_pos):  # если мышка находится в кнопке
            if self.name == 'Играть':
                choose_level()
            if self.name in ['Легкий уровень', 'Средний уровень', 'Сложный уровень']:
                if self.name == 'Легкий уровень':
                    cell_size = randint(50, 60)
                elif self.name == 'Средний уровень':
                    cell_size = randint(20, 30)
                else:
                    cell_size = randint(10, 20)
                generator = MazeGenerator(SIZE, cell_size)
                generator.main_loop()
            if self.name == 'Меню':
                OPENED_MENU = not OPENED_MENU
                open_close_menu()

    def hover(self, mouse_pos):
        if self.check_mouse_pos(mouse_pos):
            print(1)

    def check_mouse_pos(self, mouse_pos):
        """проверяет, что мышка находится внутри кнопки"""
        mouse_x, mouse_y = mouse_pos
        if mouse_x in range(self.rect.left, self.rect.right) and mouse_y in range(self.rect.top, self.rect.bottom):
            return True
        return


def choose_level():
    """выбор уровня"""
    level_image = load_image('buttons/button.png', (255, 255, 255))
    easy_level = Button(level_image, x_pos=460, y_pos=240, text='Легкий', name='Легкий уровень')
    medium_level = Button(level_image, x_pos=460, y_pos=300, text='Средний', name='Средний уровень')
    hard_level = Button(level_image, x_pos=460, y_pos=360, text='Сложный', name='Сложный уровень')
    level_buttons = [easy_level, medium_level, hard_level]
    screen.fill((0, 0, 0))
    screen.blit(maze_image, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in level_buttons:
                    btn.on_click(pygame.mouse.get_pos())
        for btn in level_buttons:
            btn.update()

        pygame.display.update()


def open_close_menu():
    """открывает или закрывает меню окно с меню"""
    if OPENED_MENU:
        points = [(SIZE[0] * 3 / 4, 0), SIZE]
        pygame.draw.rect(screen, '#2E8B57', points)
        icon_data = [('Авторизоваться', 'icons/authorise_icon.png'), ('Статистика', "icons/graphiques_icon.png"),
                     ('Инструкция', 'icons/instruction_icon.png'), ('Настройки', 'icons/settings_icon.png')]
        for i in range(4):
            image = load_image('buttons/button.png', (255, 255, 255))
            image_size = (100, 40)
            image = pygame.transform.scale(image, image_size)
            btn = Button(image=image, x_pos=850, y_pos=100 + 2 * i * image_size[1],
                         name=icon_data[i][0], icon=icon_data[i][1])
            btn.update()
    else:
        main()
    pygame.display.update()


def authorise():
    """позволяет войти или создать аккаунт"""


def statistics():
    """открывает страницу с рейтингом"""


def settings():
    """страница настроек"""


def instructions():
    """открывает страницу, где можно будет узнать об игре и потренироваться/разобраться"""


def main():
    screen.fill((0, 0, 0))
    screen.blit(maze_image, (0, 0))
    time_delta = CLOCK.tick(60) / 1000.0

    play_btn_image = load_image('buttons/play_btn_image.png', (255, 255, 255))  # картинка кнопки играть
    play_button = Button(image=play_btn_image, x_pos=460, y_pos=230, name='Играть')
    menu_image = load_image('buttons/eye_menu.png', (0, 0, 0))  # картинка кнопки меню
    menu_button = Button(image=menu_image, x_pos=SIZE[0] - 50, y_pos=40, name='Меню')
    all_buttons = [play_button, menu_button]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                confirmation_dialog = pygame_gui.windows.UIConfirmationDialog(
                    rect=pygame.Rect((250, 200), (300, 200)),
                    manager=MANAGER,
                    window_title='Подтвердите действие',
                    action_long_desc='Вы уверены, что хотите выйти?',
                    action_short_name='OK', blocking=True)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in all_buttons:
                    btn.on_click(pygame.mouse.get_pos())
            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                sys.exit()
            MANAGER.process_events(event)
        MANAGER.update(time_delta)
        for btn in all_buttons:
            btn.update()
        MANAGER.draw_ui(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
