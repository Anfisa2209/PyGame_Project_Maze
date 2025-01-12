import sqlite3

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UITextEntryLine

from main_page import maze_image, WINDOW_SIZE

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
USER_ID = 0

MANAGER = pygame_gui.UIManager(WINDOW_SIZE)
CLOCK = pygame.time.Clock()

connect = sqlite3.connect('maze_db')
cursor = connect.cursor()

entry_size = (250, 50)
name_entry = UITextEntryLine(
    relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 100), entry_size),
    manager=MANAGER, placeholder_text='Введите свой псевдоним')
password_entry = UITextEntryLine(
    relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 180), entry_size),
    manager=MANAGER, placeholder_text='Введите пароль')
password_entry.set_forbidden_characters([' '])
repeat_password_entry = UITextEntryLine(  # если регистрируются
    relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 260), entry_size),
    manager=MANAGER, placeholder_text='Повторите пароль', visible=0)
repeat_password_entry.set_forbidden_characters([' '])
log_in_btn = UIButton(relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 350), entry_size),
                      text='Войти', manager=MANAGER)
sign_in_btn = UIButton(relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 95, 430), (200, 30)),
                       text='Нет аккаунта? Создайте', manager=MANAGER)

password_text_pos = WINDOW_SIZE[0] // 2 - 125, 230  # чтобы было удобнее менять позицию текста ошибки
name_text_pos = WINDOW_SIZE[0] // 2 - 125, 150


def write_text(screen_to_write_on, text, x_pos, y_pos, size=25):
    """пишет текст"""
    screen_to_write_on.blit(maze_image, (0, 0))
    font = pygame.font.Font(None, size)
    text = font.render(text, True, (255, 0, 0))
    screen_to_write_on.blit(text, (x_pos, y_pos))


def check_password(password, repeat_password_exists=False):
    """проверяет пароль"""
    if len(password) < 8:
        write_text(screen, 'Длина не может быть меньше 8', *password_text_pos)
    elif password.isdigit():
        write_text(screen, 'Добавьте букву', *password_text_pos)
    elif not [i for i in password if i.isdigit()]:
        write_text(screen, 'Добавьте цифру', *password_text_pos)
    elif ' ' in password:
        write_text(screen, 'Уберите пробел(ы)', *password_text_pos)
    else:
        if repeat_password_exists:
            return passwords_match(password, repeat_password_entry.get_text())
        else:
            write_text(screen, '', *password_text_pos)
            return True


def passwords_match(password, second_password):
    """проверяет, что пароли совпадают"""
    if second_password != password:
        write_text(screen, 'Пароли не совпадают', *password_text_pos)
    else:
        write_text(screen, '', *password_text_pos)
        return True


def check_login(login):
    """проверяет логин"""
    if len(login) == 0:
        write_text(screen, 'Имя не может быть пустым', *name_text_pos)
        return
    if login.isspace():
        write_text(screen, 'Имя не может состоять только из пробелов', *name_text_pos)
    else:
        write_text(screen, '', *name_text_pos)
        return True


def log_in():
    """входит в аккаунт"""
    global USER_ID
    screen.blit(maze_image, (0, 0))
    repeat_password_entry.visible = 0
    sign_in_btn.set_text('Нет аккаунта? Создайте')
    log_in_btn.set_text('Войти')

    name, password = name_entry.get_text(), password_entry.get_text()
    if check_login(name) and check_password(password):
        user_id = cursor.execute('SELECT id FROM Person WHERE name = ? AND password = ?', (name, password)).fetchone()
        print("check_login", user_id)
        if user_id:
            USER_ID = user_id[0]
            from main_page import main
            main(USER_ID)
        else:
            write_text(screen, 'Неправильный логин/пароль, \nпопробуйте еще раз', *password_text_pos)


def create_account():
    """создает аккаунт"""
    global USER_ID
    repeat_password_entry.visible = 1
    sign_in_btn.set_text('Есть аккаунт? Войдите')
    log_in_btn.set_text('Зарегистрироваться')
    name, password, repeat_password = name_entry.get_text(), password_entry.get_text(), repeat_password_entry.get_text()
    password_exists = cursor.execute('SELECT id FROM Person WHERE password = ?', (password,)).fetchone()
    if check_login(name) and check_password(password, True) and password == repeat_password and not password_exists:
        cursor.execute('INSERT INTO Person (name, password, player) VALUES (?, ?, ?)', (name, password, 'ninja_player'))
        connect.commit()
        user_id = cursor.execute('SELECT id FROM Person WHERE name = ? AND password = ?',
                                 (name, password)).fetchone()[0]
        USER_ID = user_id
        from main_page import main
        main(user_id)
    if password_exists:
        write_text(screen, 'Такой пароль уже существует - придумайте другой', *password_text_pos)


def main():
    global USER_ID
    USER_ID = 0
    name_entry.set_text('')
    password_entry.set_text('')
    repeat_password_entry.set_text('')
    repeat_password_entry.visible = False
    log_in_btn.set_text(text='Войти')
    sign_in_btn.set_text(text='Нет аккаунта? Создайте')

    screen.blit(maze_image, (0, 0))
    pygame.display.set_caption('Войти/Зарегистрироваться')
    time_delta = CLOCK.tick(60) / 1000.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                from main_page import main
                print(USER_ID, 'go to main from quit authorise_window')
                main(USER_ID)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == log_in_btn:
                    # если сейчас на кнопке написано "Зарегистрироваться" и на нее нажали,
                    # то вызывается функция create_account; иначе, если написано "Войти", оно входит
                    create_account() if log_in_btn.text == 'Зарегистрироваться' else log_in()
                if event.ui_element == sign_in_btn:
                    log_in() if sign_in_btn.text == 'Есть аккаунт? Войдите' else create_account()
            MANAGER.process_events(event)

        MANAGER.update(time_delta)
        MANAGER.draw_ui(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
