import pygame
import sqlite3
import pygame_gui
from pygame_gui.elements import UIButton, UITextEntryLine, UILabel

from main_page import load_image, WINDOW_SIZE

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
maze_image = load_image('maze_fon.jpg', (255, 255, 255))
screen.blit(maze_image, (0, 0))

MANAGER = pygame_gui.UIManager(WINDOW_SIZE)
CLOCK = pygame.time.Clock()
entry_size = (250, 50)
name_entry = UITextEntryLine(
    relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 100), entry_size),
    manager=MANAGER, placeholder_text='Введите свой псевдоним')
password_entry = UITextEntryLine(
    relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 200), entry_size),
    manager=MANAGER, placeholder_text='Введите пароль')
repeat_password_entry = UITextEntryLine(  # если регистрируются
    relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 300), entry_size),
    manager=MANAGER, placeholder_text='Повторите пароль', visible=0)

log_in_btn = UIButton(relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 350), entry_size),
                      text='Войти', manager=MANAGER)
password_error_lbl = UILabel(relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 250), entry_size),
                             manager=MANAGER, text='')
connect = sqlite3.connect('maze_db')
cursor = connect.cursor()


def check_password(password, second_password=''):
    global password_error_lbl
    if len(password) < 8:
        password_error_lbl.set_text('Длина не может быть меньше 8!')

    elif password.isdigit():
        password_error_lbl.set_text('Добавьте букву!')
    elif not [i for i in password if i.isdigit()]:
        password_error_lbl.set_text('Добавьте цифру!')
    elif ' ' in password:
        password_error_lbl.set_text('Уберите пробел!')
    return True


def check_login(name):
    print(name)


def main():
    screen.fill((0, 0, 0))
    screen.blit(maze_image, (0, 0))
    pygame.display.set_caption('Войти/Зарегистрироваться')
    time_delta = CLOCK.tick(60) / 1000.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                from main_page import main
                main()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == log_in_btn:
                    name, password = name_entry.get_text(), password_entry.get_text()
                    if check_login(name) and check_password(password):
                        request = '''INSERT INTO Person (name, password) VALUES (?, ?)'''
                        cursor.execute(request, (name, password))

            MANAGER.process_events(event)

        MANAGER.update(time_delta)
        MANAGER.draw_ui(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
