import sys

import pygame
from pygame_gui.elements import UIButton, UITextEntryLine
import pygame_gui
from main_page import WINDOW_SIZE, maze_image, CLOCK, cursor, connect

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
entry_size = (250, 50)
MANAGER = pygame_gui.UIManager(WINDOW_SIZE)
USER_ID = 0
name_entry = UITextEntryLine(pygame.Rect((100, 100), entry_size), MANAGER)
name_entry.is_enabled = False
password_entry = UITextEntryLine(pygame.Rect((100, 180), entry_size), MANAGER)
password_entry.is_enabled = False
exit_button = UIButton(pygame.Rect(((WINDOW_SIZE[0] - 300, WINDOW_SIZE[1] - 250), entry_size)), 'Выйти из аккаунта',
                       MANAGER)
# кнопка для изменения пароля/имени V
change_data_button = UIButton(pygame.Rect((150 + password_entry.rect[0], 260), (100, 50)), 'Изменить', MANAGER)
delete_account_button = UIButton(pygame.Rect(((WINDOW_SIZE[0] - 300, WINDOW_SIZE[1] - 300), entry_size)),
                                 'Удалить аккаунт', MANAGER)
cancel_button = UIButton(pygame.Rect((50 + password_entry.rect[0], 275), (100, 35)), 'Отмена', MANAGER, visible=0)
exit_account_txt, delete_account_txt = 'Вы уверены, что хотите выйти из аккаунта?', 'Вы уверены, что хотите удалить аккаунт?'
exit_account = delete_account = close_game = None


def create_confirmation_window(text):
    '''окно для подтверждения на удаление/выход из аккаунта'''
    confirmation_window = pygame_gui.windows.UIConfirmationDialog(rect=pygame.Rect((250, 200), (300, 200)),
                                                                  manager=MANAGER,
                                                                  window_title='Подтвердите действие',
                                                                  action_long_desc=text)
    return confirmation_window


def main(user_id):
    global USER_ID, exit_account, delete_account, close_game
    USER_ID = user_id
    screen.blit(maze_image, (0, 0))
    pygame.display.set_caption('Личный кабинет')
    time_delta = CLOCK.tick(60) / 1000.0
    login, password = cursor.execute('''SELECT name, password FROM Person WHERE id = ?''', (USER_ID,)).fetchone()
    name_entry.set_text(login)
    password_entry.set_text(password)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game = create_confirmation_window('Вы уверены, что хотите выйти?')
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                cancel_button.visible = 0
                if event.ui_element == exit_button:
                    exit_account = create_confirmation_window(exit_account_txt)
                if event.ui_element == delete_account_button:
                    delete_account = create_confirmation_window(delete_account_txt)
                if event.ui_element == cancel_button:
                    change_data_button.set_text('Изменить')
                    name_entry.is_enabled = False
                    password_entry.is_enabled = False
                if event.ui_element == change_data_button:
                    cancel_button.visible = 1
                    if change_data_button.text == 'Изменить':
                        change_data_button.set_text('Сохранить')
                        name_entry.is_enabled = True
                        password_entry.is_enabled = True
                    else:
                        from authorise_window import check_login, check_password
                        change_data_button.set_text('Изменить')
                        name_entry.is_enabled = False
                        password_entry.is_enabled = False

                        new_login, new_password = name_entry.get_text(), password_entry.get_text()
                        login_exists = cursor.execute('''SELECT id FROM Person WHERE name = ?''',
                                                      (new_login,)).fetchone()
                        if check_login(new_login) and check_password(new_password) and not login_exists:
                            cursor.execute('''UPDATE Person SET name = ?, password = ? WHERE id = ?''',
                                           (new_login, new_password, USER_ID))
                            print(new_login, new_password, )
                            connect.commit()
                        else:
                            name_entry.set_text(login)
                            password_entry.set_text(password)
                            error_text = ''
                            if login_exists:
                                print(1)
                                error_text = 'Такой логин уже существует'
                            if not check_login(login):
                                print(2)
                                error_text = 'Логин не соответствует правилам'
                            if not check_password(password):
                                print(3)
                                error_text = 'Пароль не соответствует правилам'
                            create_confirmation_window(error_text)

            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                from main_page import main as go_to_main
                if event.ui_element == exit_account:
                    go_to_main(0)
                if event.ui_element == delete_account:
                    cursor.execute('''DELETE FROM Person WHERE id = ?''', (USER_ID,))
                    connect.commit()
                    go_to_main(0)
                if event.ui_element == close_game:
                    sys.exit()

            MANAGER.process_events(event)
        screen.blit(maze_image, (0, 0))
        MANAGER.update(time_delta)
        MANAGER.draw_ui(screen)
        pygame.display.update()


if __name__ == '__main__':
    main(28)
