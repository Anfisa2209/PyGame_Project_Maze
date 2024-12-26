import os
import sys
from random import randint

import pygame
import pygame_gui
from generate_maze import MazeGenerator


def load_image(task, colorkey=None):
    fulltask = os.path.join('data', task)
    if not os.path.isfile(fulltask):
        print(f"Файл с изображением '{fulltask}' не найден")
        sys.exit()
    image = pygame.image.load(fulltask)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


pygame.init()
WINDOW_SIZE = (967, 560)
OPENED_MENU = False  # открыто ли сейчас окно меню
screen = pygame.display.set_mode(WINDOW_SIZE)
maze_image = load_image('maze_fon.jpg', (255, 255, 255))
MANAGER = pygame_gui.UIManager(WINDOW_SIZE)
CLOCK = pygame.time.Clock()
screen.blit(maze_image, (0, 0))


class Button:
    """Класс кнопки"""

    def __init__(self, image, x_pos, y_pos, task, text='', font_size=20, icon=''):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.task = task
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
            if self.task == 'Играть':
                choose_level()
            if self.task in ['Легкий уровень', 'Средний уровень', 'Сложный уровень']:
                if self.task == 'Легкий уровень':
                    cell_size = randint(50, 60)
                elif self.task == 'Средний уровень':
                    cell_size = randint(20, 30)
                else:
                    cell_size = randint(10, 20)
                generator = MazeGenerator(WINDOW_SIZE, cell_size)
                generator.main_loop()
            if self.task == 'Меню':
                OPENED_MENU = not OPENED_MENU
                open_close_menu()
            if self.task == 'Выйти':
                print(1)
                do_exit()

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
    easy_level = Button(level_image, x_pos=460, y_pos=240, text='Легкий', task='Легкий уровень')
    medium_level = Button(level_image, x_pos=460, y_pos=300, text='Средний', task='Средний уровень')
    hard_level = Button(level_image, x_pos=460, y_pos=360, text='Сложный', task='Сложный уровень')
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
        points = [(WINDOW_SIZE[0] * 3 / 4, 0), WINDOW_SIZE]
        pygame.draw.rect(screen, '#2E8B57', points)
        icon_data = [('Авторизоваться', 'icons/authorise_icon.png'), ('Статистика', "icons/graphiques_icon.png"),
                     ('Инструкция', 'icons/instruction_icon.png'), ('Настройки', 'icons/settings_icon.png')]
        exit_image = pygame.transform.scale(load_image('buttons/button.png', -1), (200, 70))
        exit_btn = Button(image=exit_image, x_pos=WINDOW_SIZE[0] - exit_image.get_width() // 2,
                          y_pos=WINDOW_SIZE[1] - exit_image.get_height(), text='ВЫХОД', font_size=30, task='Выйти')
        exit_btn.update()
        buttons = []
        for i in range(4):
            """создает кнопки во вкладке меню"""
            image = load_image('buttons/button.png', (255, 255, 255))
            image_size = (100, 40)
            image = pygame.transform.scale(image, image_size)
            btn = Button(image=image, x_pos=850, y_pos=100 + 2 * i * image_size[1],
                         task=icon_data[i][0], icon=icon_data[i][1])
            buttons.append(btn)
        for btn in buttons:
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


def do_exit():
    '''показывает окошко, которое спрашивает у пользователя, действительно ли он хочет выйти'''
    pygame_gui.windows.UIConfirmationDialog(
        rect=pygame.Rect((250, 200), (300, 200)),
        manager=MANAGER,
        window_title='Подтвердите действие',
        action_long_desc='Вы уверены, что хотите выйти?',
        action_short_name='OK', blocking=True)


def main():
    screen.fill((0, 0, 0))
    screen.blit(maze_image, (0, 0))
    time_delta = CLOCK.tick(60) / 1000.0

    play_btn_image = load_image('buttons/play_btn_image.png', (255, 255, 255))  # картинка кнопки играть
    play_button = Button(image=play_btn_image, x_pos=WINDOW_SIZE[0] // 2,
                         y_pos=(WINDOW_SIZE[1] - play_btn_image.get_height()) // 2, task='Играть')
    menu_image = load_image('buttons/eye_menu.png', (0, 0, 0))  # картинка кнопки меню
    menu_button = Button(image=menu_image, x_pos=WINDOW_SIZE[0] - 50, y_pos=40, task='Меню')
    all_buttons = [play_button, menu_button]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                do_exit()
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