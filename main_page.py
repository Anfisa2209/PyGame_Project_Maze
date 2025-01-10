import os
import sys
from random import randint
import sqlite3

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
WINDOW_SIZE = (950, 560)
OPENED_MENU = CONFIRMATION_WINDOW_EXISTS = False  # открыто ли сейчас окно меню и есть ли окно для подтверждения
screen = pygame.display.set_mode(WINDOW_SIZE)
maze_image = load_image('maze_fon.jpg', (255, 255, 255))
MANAGER = pygame_gui.UIManager(WINDOW_SIZE)
CLOCK = pygame.time.Clock()
screen.blit(maze_image, (0, 0))
exit_btn = authorise_btn = settings_btn = statistics_btn = instructions_btn = confirmation_window = None
cur_player_rect = player1_rect = player2_rect = []  # список координат картинок карточек
USER_ID = 0
connect = sqlite3.connect('maze_db')
cursor = connect.cursor()
players_pos = {'current': 'ninja_player', 'small_player1': 'elf_player', 'small_player2': 'black_player'}


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
        if self.check_mouse_pos(mouse_pos) and not CONFIRMATION_WINDOW_EXISTS:  # если мышка находится в кнопке
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
                show_confirmation_window()
            if self.task == 'Авторизоваться':
                if not USER_ID:
                    from authorise_window import main as authorise_main
                    OPENED_MENU = False
                    authorise_main()
            if self.task == 'карта игрока':
                self.update()
                edit_current_player()

    def check_mouse_pos(self, mouse_pos):
        """проверяет, что мышка находится внутри кнопки"""
        mouse_x, mouse_y = mouse_pos
        if mouse_x in range(self.rect.left, self.rect.right) and mouse_y in range(self.rect.top, self.rect.bottom):
            return True
        return


def edit_current_player():
    """меняет текущего песонажа"""
    global players_pos
    x, y = pygame.mouse.get_pos()
    if (x in range(cur_player_rect[0], cur_player_rect[0] + cur_player_rect[2])
            and y in range(cur_player_rect[1], cur_player_rect[1] + cur_player_rect[3])):
        pass
    if (x in range(player1_rect[0], player1_rect[0] + player1_rect[2])
            and y in range(player1_rect[1], player1_rect[1] + player1_rect[3])):
        players_pos['current'], players_pos['small_player1'] = players_pos['small_player1'], players_pos['current']
    if (x in range(player2_rect[0], player2_rect[0] + player2_rect[2])
            and y in range(player2_rect[1], player2_rect[1] + player2_rect[3])):
        players_pos['current'], players_pos['small_player2'] = players_pos['small_player2'], players_pos['current']
    if USER_ID:
        cursor.execute('''UPDATE Person SET player = ? WHERE id = ?''', (players_pos['current'], USER_ID))
        connect.commit()


def choose_level():
    """выбор уровня"""
    global OPENED_MENU
    level_image = load_image('buttons/button.png', (255, 255, 255))
    easy_level = Button(level_image, x_pos=460, y_pos=240, text='Легкий', task='Легкий уровень')
    medium_level = Button(level_image, x_pos=460, y_pos=300, text='Средний', task='Средний уровень')
    hard_level = Button(level_image, x_pos=460, y_pos=360, text='Сложный', task='Сложный уровень')
    level_buttons = [easy_level, medium_level, hard_level]
    screen.blit(maze_image, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                OPENED_MENU = False
                main(USER_ID)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in level_buttons:
                    btn.on_click(pygame.mouse.get_pos())
        for btn in level_buttons:
            btn.update()

        pygame.display.update()


def open_close_menu():
    """открывает или закрывает меню окно с меню"""
    global exit_btn, authorise_btn, settings_btn, statistics_btn, instructions_btn
    if OPENED_MENU:
        points = [(WINDOW_SIZE[0] * 3 / 4, 0), WINDOW_SIZE]
        pygame.draw.rect(screen, '#2E8B57', points)
        exit_image = pygame.transform.scale(load_image('buttons/button.png', -1), (200, 70))
        exit_btn = Button(image=exit_image, x_pos=WINDOW_SIZE[0] - exit_image.get_width() // 2,
                          y_pos=WINDOW_SIZE[1] - exit_image.get_height(), text='ВЫЙТИ', font_size=30, task='Выйти')

        button_image = load_image('buttons/button.png', (255, 255, 255))
        image_size = (100, 40)
        button_image = pygame.transform.scale(button_image, image_size)

        authorise_btn = Button(image=button_image, x_pos=850, y_pos=150, task='Авторизоваться',
                               icon='icons/authorise_icon.png')
        settings_btn = Button(image=button_image, x_pos=850, y_pos=210, task='Настройки',
                              icon='icons/settings_icon.png')
        statistics_btn = Button(image=button_image, x_pos=850, y_pos=260, task='Статистика',
                                icon='icons/graphiques_icon.png')
        instructions_btn = Button(image=button_image, x_pos=850, y_pos=320, task='Инструкция',
                                  icon='icons/instruction_icon.png')

    else:
        authorise_btn = settings_btn = statistics_btn = instructions_btn = None
        main(USER_ID)


def show_confirmation_window():
    '''показывает окошко, которое спрашивает у пользователя, действительно ли он хочет выйти'''
    global CONFIRMATION_WINDOW_EXISTS, confirmation_window
    confirmation_window = pygame_gui.windows.UIConfirmationDialog(
        rect=pygame.Rect((250, 200), (300, 200)),
        manager=MANAGER,
        window_title='Подтвердите действие',
        action_long_desc='Вы уверены, что хотите выйти?')
    CONFIRMATION_WINDOW_EXISTS = True
    event = pygame.event.poll()
    if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
        sys.exit()


def main(user_id):
    global USER_ID, CONFIRMATION_WINDOW_EXISTS, cur_player_rect, player1_rect, player2_rect, players_pos
    USER_ID = user_id
    pygame.display.set_caption('Главная страница')
    screen.blit(maze_image, (0, 0))
    time_delta = CLOCK.tick(60) / 1000.0

    play_btn_image = load_image('buttons/play_btn_image.png', (255, 255, 255))  # картинка кнопки играть
    play_button = Button(image=play_btn_image, x_pos=WINDOW_SIZE[0] // 2,
                         y_pos=(WINDOW_SIZE[1] - play_btn_image.get_height()) // 2, task='Играть')
    menu_image = load_image('buttons/eye_menu.png', -1)  # картинка кнопки меню
    menu_button = Button(image=menu_image, x_pos=WINDOW_SIZE[0] - 50, y_pos=40, task='Меню')
    cur_player_card = Button(load_image('cards/player_card.png', -1), x_pos=150, y_pos=WINDOW_SIZE[0] / 4,
                             task='карта игрока')

    small_card_image = pygame.transform.scale(load_image('cards/player_card.png', -1), (100, 100))
    small_player_card1 = Button(small_card_image, x_pos=95, y_pos=430, task='карта игрока')
    small_player_card2 = Button(small_card_image,
                                x_pos=small_player_card1.image.get_width() + small_player_card1.x_pos + 5,
                                y_pos=430, task='карта игрока')
    cur_player_rect, player1_rect, player2_rect = cur_player_card.rect, small_player_card1.rect, small_player_card2.rect
    players_images = list(players_pos.values())  # получаем всех игроков
    player = cursor.execute('''SELECT player FROM Person WHERE id = ?''', (USER_ID,)).fetchone()[
        0] if USER_ID else 'ninja_player'
    players_images.remove(player)  # удаляем текущего - в списке только игроки для маленьких карточек
    players_pos = {'current': player, 'small_player1': players_images[0], 'small_player2': players_images[1]}

    all_buttons = [play_button, menu_button, cur_player_card, small_player_card1, small_player_card2, ]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                show_confirmation_window()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in all_buttons:
                    btn.on_click(pygame.mouse.get_pos())
                if CONFIRMATION_WINDOW_EXISTS:
                    cancel_x, cancel_y, cancel_width, cancel_height = confirmation_window.cancel_button.rect
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    close_x, close_y, close_width, close_height = confirmation_window.close_window_button.rect
                    if (mouse_x in range(cancel_x, cancel_x + cancel_width) and
                        mouse_y in range(cancel_y, cancel_y + cancel_height)) or \
                            (mouse_x in range(close_x, close_x + close_width)
                             and mouse_y in range(close_y, close_y + close_height)):
                        CONFIRMATION_WINDOW_EXISTS = False
            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                sys.exit()
            MANAGER.process_events(event)
        screen.blit(maze_image, (0, 0))
        pygame.draw.rect(screen, '#2E8B57', [(WINDOW_SIZE[0] * 3 / 4, 0), WINDOW_SIZE]) if OPENED_MENU else None
        if OPENED_MENU:
            all_buttons.extend((exit_btn, authorise_btn, settings_btn, statistics_btn, instructions_btn))
        MANAGER.update(time_delta)
        for btn in all_buttons:
            btn.update()
        current_player_image = Button(pygame.transform.scale(load_image(f'players/{players_pos["current"]}.png', -1),
                                                             (200, 200)), 145, WINDOW_SIZE[0] / 4, task='')
        small_player1 = Button(load_image(f'players/{players_pos["small_player1"]}.png', -1), 95, 430, task='')
        small_player2 = Button(load_image(f'players/{players_pos["small_player2"]}.png', -1),
                               small_player_card1.image.get_width() + small_player_card1.x_pos + 5, 430, task='')
        current_player_image.update()
        small_player1.update()
        small_player2.update()
        MANAGER.draw_ui(screen)
        pygame.display.update()


if __name__ == '__main__':
    main(USER_ID)
