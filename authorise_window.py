import sqlite3

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UITextEntryLine

from main_page import load_image, WINDOW_SIZE

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
maze_image = load_image('maze_fon.jpg', (255, 255, 255))
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
repeat_password_entry = UITextEntryLine(  # если регистрируются
    relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 260), entry_size),
    manager=MANAGER, placeholder_text='Повторите пароль', visible=0)

log_in_btn = UIButton(relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 125, 350), entry_size),
                      text='Войти', manager=MANAGER)
sign_in_btn = UIButton(relative_rect=pygame.Rect((WINDOW_SIZE[0] // 2 - 95, 430), (200, 30)),
                       text='Нет аккаунта? Создайте', manager=MANAGER)

password_error_text = name_error_text = ''


def write_text(text, x_pos, y_pos, size=25):
    screen.blit(maze_image, (0, 0))
    font = pygame.font.Font(None, size)
    text = font.render(text, True, (255, 0, 0))
    screen.blit(text, (x_pos, y_pos))


def check_password(password):
    global password_error_text
    if len(password) < 8:
        password_error_text = 'Длина не может быть меньше 8'
        return
    elif password.isdigit():
        password_error_text = 'Добавьте букву'
        return
    elif not [i for i in password if i.isdigit()]:
        password_error_text = 'Добавьте цифру'
        return
    elif ' ' in password:
        password_error_text = 'Уберите пробел(ы)'
        return
    else:
        password_error_text = ''
        return True


def check_login(login):
    global name_error_text
    if len(login) == 0:
        write_text('Имя не может быть пустым', WINDOW_SIZE[0] // 2 - 125, 150)
        return
    if not login.replace(' ', ''):
        write_text('Имя не может состоять только из пробелов', WINDOW_SIZE[0] // 2 - 125, 150)
    else:
        name_error_text = ''
        return True


def log_in():
    global USER_ID
    screen.blit(maze_image, (0, 0))
    repeat_password_entry.visible = 0
    sign_in_btn.set_text('Нет аккаунта? Создайте')
    log_in_btn.set_text('Войти')

    name, password = name_entry.get_text(), password_entry.get_text()
    if not check_login(name):
        write_text(name_error_text, WINDOW_SIZE[0] // 2 - 125, 70)
    if not check_password(password):
        write_text(password_error_text, WINDOW_SIZE[0] // 2 - 125, 230)
    if check_login(name) and check_password(password):
        sql_request = '''SELECT id FROM Person WHERE name = ? AND password = ?'''
        user_id = cursor.execute(sql_request, (name, password)).fetchone()
        USER_ID = user_id
        if user_id:
            from main_page import main
            main(USER_ID)
        else:
            write_text('Неправильный логин/пароль, \nпопробуйте еще раз', WINDOW_SIZE[0] // 2 - 125, 230)


def create_account():
    global USER_ID
    repeat_password_entry.visible = 1
    sign_in_btn.set_text('Есть аккаунт? Войдите')
    log_in_btn.set_text('Зарегистрироваться')
    name, password, repeat_password = name_entry.get_text(), password_entry.get_text(), repeat_password_entry.get_text()
    if not check_login(name):
        write_text(name_error_text, WINDOW_SIZE[0] // 2 - 125, 70)
    if not check_password(password):
        write_text(password_error_text, WINDOW_SIZE[0] // 2 - 125, 230)
    if repeat_password != password:
        write_text('Пароли не совпадают', WINDOW_SIZE[0] // 2 - 125, 230)
    if check_login(name) and check_password(password) and password == repeat_password:
        sql_request = '''INSERT INTO Person (name, password, player) VALUES (?, ?, ?)'''
        cursor.execute(sql_request, (name, password, 'first_player'))
        connect.commit()
        user_id = cursor.execute('''SELECT id FROM Person WHERE name = ? AND password = ?''',
                                 (name, password)).fetchone()[0]
        USER_ID = user_id
        from main_page import main
        main(user_id)


def main():
    screen.blit(maze_image, (0, 0))
    pygame.display.set_caption('Войти/Зарегистрироваться')
    time_delta = CLOCK.tick(60) / 1000.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                from main_page import main
                main(USER_ID)
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == name_entry:
                    check_login(name_entry.get_text())
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == log_in_btn:
                    # если сейчас на кнопке написано "Зарегистрироваться" и на нее нажали,
                    # то вызывается функция create_account; иначе, если написано "Войти", оно входит
                    if log_in_btn.text == 'Зарегистрироваться':
                        create_account()
                    else:
                        log_in()
                if event.ui_element == sign_in_btn:
                    if sign_in_btn.text == 'Есть аккаунт? Войдите':
                        log_in()
                    else:
                        create_account()

            MANAGER.process_events(event)

        MANAGER.update(time_delta)
        MANAGER.draw_ui(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
