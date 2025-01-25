import os
import sys
import sqlite3

import pygame
import pygame_gui

import authorise_window
import game_code
from game_code import start_game, play_music


def load_image(task, colorkey=None):
    fulltask = os.path.join('data', task)
    if not os.path.isfile(fulltask):
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
WINDOW_SIZE = WIDTH, HEIGHT = 950, 560
screen = pygame.display.set_mode(WINDOW_SIZE)
maze_image = load_image('maze_fon.jpg', (255, 255, 255))
button_image = load_image('buttons/button.png', -1)
MANAGER = pygame_gui.UIManager(WINDOW_SIZE)
CLOCK = pygame.time.Clock()
screen.blit(maze_image, (0, 0))
time_delta = CLOCK.tick(60) / 1000.0

OPENED_MENU = CONFIRMATION_WINDOW_EXISTS = False  # открыто ли сейчас окно меню и есть ли окно для подтверждения
exit_btn = authorise_btn = statistics_btn = instructions_btn = confirmation_window = None
cur_player_rect = player1_rect = player2_rect = []  # список координат картинок карточек
exit_game_text = 'Вы уверены, что хотите выйти из игры?'
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
        global OPENED_MENU, confirmation_window, CONFIRMATION_WINDOW_EXISTS
        if self.check_mouse_pos(mouse_pos) and not CONFIRMATION_WINDOW_EXISTS:  # если мышка находится в кнопке
            if self.task == 'Играть':
                choose_level()
            if self.task in ['Легкий уровень', 'Средний уровень', 'Сложный уровень']:
                # простой - 60, средний - 50, сложный - 40
                if self.task == 'Легкий уровень':
                    cell_size = 60
                    difficulty = 1
                elif self.task == 'Средний уровень':
                    cell_size = 50
                    difficulty = 2
                else:
                    cell_size = 40
                    difficulty = 3
                player_pic_name = 'players/' + players_pos['current'] + '/' + players_pos['current'] + '_walk_right.png'
                start_game(cell_size, difficulty, player_pic_name, USER_ID)
            if self.task == 'Меню':
                OPENED_MENU = not OPENED_MENU
                open_close_menu()
            if self.task == 'Выйти':
                confirmation_window = create_confirmation_window('Подтверждение', exit_game_text, MANAGER)
                CONFIRMATION_WINDOW_EXISTS = True
                check_confirmation_window(confirmation_window)
            if self.task == 'Авторизоваться':
                if USER_ID == 0:
                    from authorise_window import main as authorise_main
                    OPENED_MENU = False
                    authorise_main()
                else:
                    from personal_account import main
                    main(USER_ID)
            if self.task == 'карта игрока':
                edit_current_player()
            if self.task == 'Статистика':
                statistic()
            if self.task == 'Инструкция':
                instruction()

    def check_mouse_pos(self, mouse_pos):
        """Проверяет, что мышка находится внутри кнопки"""
        mouse_x, mouse_y = mouse_pos
        if mouse_x in range(self.rect.left, self.rect.right) and mouse_y in range(self.rect.top, self.rect.bottom):
            return True
        return


def edit_current_player():
    # меняет текущего персонажа
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


def statistic():
    # окно, где пользователь может посмотреть свои успехи в игре
    global confirmation_window, CONFIRMATION_WINDOW_EXISTS
    pygame.display.set_caption('Статистика')
    manager = pygame_gui.UIManager(WINDOW_SIZE)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                CONFIRMATION_WINDOW_EXISTS = True
                confirmation_window = create_confirmation_window('Подтверждение', exit_game_text, manager)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if go_back.check_mouse_pos(pygame.mouse.get_pos()) and not CONFIRMATION_WINDOW_EXISTS:
                    main(USER_ID)
                if CONFIRMATION_WINDOW_EXISTS:
                    check_confirmation_window(confirmation_window)
            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                terminate()
            manager.process_events(event)
        screen.blit(maze_image, (0, 0))
        if not USER_ID:
            font = pygame.font.Font(None, 30)
            text = font.render('Вы не зарегистрированы', True, 'red')
            screen.blit(text, (340, 250))
        else:
            request = 'SELECT cherries, time FROM Statistic JOIN Person ON user_id = ? WHERE id = ?'
            cherry_eaten = cursor.execute('SELECT max_cherry FROM Statistic JOIN Person ON user_id = ? WHERE id = ?',
                                          (USER_ID, USER_ID)).fetchone()[0]
            cherry, time = cursor.execute(request, (USER_ID, USER_ID)).fetchone()

            lines = [f'Вы потратили {time} (мин) времени в игре',
                     f"Ваш рекорд по вишенкам: {cherry_eaten}",
                     f'За все время вы съели {cherry} {game_code.change_word_form("вишенка", cherry)}']
            write(lines, pygame.font.Font(None, 50), 100)
        go_back.update()
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.update()


def write(instruction_text, font, text_coord):
    # пишет текст инструкции
    for line in instruction_text:
        string_rendered = font.render(line, True, (242, 162, 58))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


def instruction():
    global confirmation_window, CONFIRMATION_WINDOW_EXISTS
    # окно с инструкцией
    # текст инструкции находится в файле instruction.txt
    pygame.display.set_caption('Инструкция')
    manager = pygame_gui.UIManager(WINDOW_SIZE)
    instruction_text = open('instruction.txt', encoding='utf-8', mode='r').readlines()
    font = pygame.font.Font(None, 30)
    text_coord = 10

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                CONFIRMATION_WINDOW_EXISTS = True
                confirmation_window = create_confirmation_window('Подтверждение', exit_game_text, manager)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if go_back.check_mouse_pos(pygame.mouse.get_pos()) and not CONFIRMATION_WINDOW_EXISTS:
                    main(USER_ID)
                if CONFIRMATION_WINDOW_EXISTS:
                    check_confirmation_window(confirmation_window)
            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                terminate()
            manager.process_events(event)

        screen.blit(maze_image, (0, 0))
        write(instruction_text, font, text_coord)
        go_back.update()
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()


def choose_level():
    """Выбор уровня"""
    global OPENED_MENU, confirmation_window, CONFIRMATION_WINDOW_EXISTS
    easy_level = Button(button_image, x_pos=460, y_pos=240, text='Легкий', task='Легкий уровень')
    medium_level = Button(button_image, x_pos=460, y_pos=300, text='Средний', task='Средний уровень')
    hard_level = Button(button_image, x_pos=460, y_pos=360, text='Сложный', task='Сложный уровень')
    buttons = [easy_level, medium_level, hard_level]

    screen.blit(maze_image, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                CONFIRMATION_WINDOW_EXISTS = True
                confirmation_window = create_confirmation_window('Подтверждение', exit_game_text, MANAGER)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    btn.on_click(pygame.mouse.get_pos())
                if go_back.check_mouse_pos(pygame.mouse.get_pos()) and not CONFIRMATION_WINDOW_EXISTS:
                    main(USER_ID)
                if CONFIRMATION_WINDOW_EXISTS:
                    check_confirmation_window(confirmation_window)

            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                terminate()
            MANAGER.process_events(event)
        screen.blit(maze_image, (0, 0))
        for btn in buttons:
            btn.update()
        go_back.update()
        MANAGER.update(time_delta)
        MANAGER.draw_ui(screen)
        pygame.display.update()


def open_close_menu():
    """Открывает или закрывает окно с меню"""
    global exit_btn, authorise_btn, settings_btn, statistics_btn, instructions_btn
    if OPENED_MENU:
        points = [(screen.width * 3 / 4, 0), screen.size]
        pygame.draw.rect(screen, '#2E8B57', points)
        exit_image = pygame.transform.scale(button_image, (200, 70))
        exit_btn = Button(image=exit_image, x_pos=WIDTH - exit_image.get_width() // 2,
                          y_pos=HEIGHT - exit_image.get_height(), text='ВЫЙТИ', font_size=30, task='Выйти')

        image_size = (100, 40)
        small_button_image = pygame.transform.scale(button_image, image_size)
        authorise_btn = Button(image=small_button_image, x_pos=850, y_pos=150, task='Авторизоваться',
                               icon='icons/authorise_icon.png')
        statistics_btn = Button(image=small_button_image, x_pos=850, y_pos=210, task='Статистика',
                                icon='icons/graphiques_icon.png')
        instructions_btn = Button(image=small_button_image, x_pos=850, y_pos=260, task='Инструкция',
                                  icon='icons/instruction_icon.png')

    else:
        authorise_btn = statistics_btn = instructions_btn = None
        main(USER_ID)


def terminate():
    pygame.quit()
    sys.exit()


def create_confirmation_window(window_title, text, manager):
    # окно для подтверждения на удаление/выход из аккаунта
    return pygame_gui.windows.UIConfirmationDialog(rect=pygame.Rect((250, 200), (300, 200)),
                                                   manager=manager,
                                                   window_title=window_title,
                                                   action_long_desc=text)


def check_confirmation_window(confirm_window):
    # проверяет, что нажали выход или отмена, и меняет состояние CONFIRMATION_WINDOW_EXISTS
    global CONFIRMATION_WINDOW_EXISTS
    try:
        cancel_x, cancel_y, cancel_width, cancel_height = confirm_window.cancel_button.rect
        mouse_x, mouse_y = pygame.mouse.get_pos()
        close_x, close_y, close_width, close_height = confirm_window.close_window_button.rect
        if (mouse_x in range(cancel_x, cancel_x + cancel_width) and
            mouse_y in range(cancel_y, cancel_y + cancel_height)) or \
                (mouse_x in range(close_x, close_x + close_width)
                 and mouse_y in range(close_y, close_y + close_height)):
            CONFIRMATION_WINDOW_EXISTS = False
    except AttributeError:
        CONFIRMATION_WINDOW_EXISTS = False


def main(user_id):
    global USER_ID, CONFIRMATION_WINDOW_EXISTS, cur_player_rect, player1_rect, player2_rect, players_pos, \
        confirmation_window, screen
    screen = pygame.display.set_mode(WINDOW_SIZE)
    USER_ID = user_id
    pygame.display.set_caption('Главная страница')
    screen.blit(maze_image, (0, 0))

    play_btn_image = load_image('buttons/play_btn_image.png', (255, 255, 255))  # картинка кнопки играть
    play_button = Button(image=play_btn_image, x_pos=WIDTH // 2,
                         y_pos=(HEIGHT - play_btn_image.get_height()) // 2, task='Играть')
    menu_image = load_image('buttons/eye_menu.png', -1)  # картинка кнопки меню
    menu_button = Button(image=menu_image, x_pos=screen.width - 50, y_pos=40, task='Меню')
    cur_player_card = Button(load_image('cards/player_card.png', -1), x_pos=150, y_pos=WIDTH / 4,
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

    all_buttons = [play_button, menu_button, cur_player_card, small_player_card1, small_player_card2]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                CONFIRMATION_WINDOW_EXISTS = True
                confirmation_window = create_confirmation_window('Подтверждение',
                                                                 exit_game_text, MANAGER)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in all_buttons:
                    btn.on_click(pygame.mouse.get_pos())
                if CONFIRMATION_WINDOW_EXISTS:
                    check_confirmation_window(confirmation_window)
            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                terminate()
            MANAGER.process_events(event)

        screen.blit(maze_image, (0, 0))
        if OPENED_MENU:
            all_buttons.extend((exit_btn, authorise_btn, statistics_btn, instructions_btn))
            pygame.draw.rect(screen, '#2E8B57', [(WIDTH * 3 / 4, 0), screen.size])
        MANAGER.update(time_delta)
        for btn in all_buttons:
            btn.update()
        current_player_image = Button(pygame.transform.scale(load_image(f'players/{players_pos["current"]}.png', -1),
                                                             (200, 200)), 145, WIDTH / 4, task='')
        small_player1 = Button(load_image(f'players/{players_pos["small_player1"]}.png', -1), 95, 430, task='')
        small_player2 = Button(load_image(f'players/{players_pos["small_player2"]}.png', -1),
                               small_player_card1.image.get_width() + small_player_card1.x_pos + 5, 430, task='')
        current_player_image.update()
        small_player1.update()
        small_player2.update()
        MANAGER.draw_ui(screen)
        pygame.display.update()


go_back = Button(pygame.transform.scale(button_image, (100, 50)), 70, 35, text='Назад', task='вернуться назад')

if __name__ == '__main__':
    song = play_music('music.mp3', True)
    INF = 9999
    song.play(INF)
    main(USER_ID)
