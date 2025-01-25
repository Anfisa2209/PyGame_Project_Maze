import pygame
from pygame_gui.elements import UIButton, UITextEntryLine
import pygame_gui
from main_page import WINDOW_SIZE, CLOCK, cursor, connect, create_confirmation_window, terminate, maze_image, go_back
from main_page import exit_game_text

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
entry_size = (250, 50)
MANAGER = pygame_gui.UIManager(WINDOW_SIZE)
USER_ID = 0
name_entry = UITextEntryLine(pygame.Rect((100, 100), entry_size), MANAGER)
name_entry.is_enabled = False
password_entry = UITextEntryLine(pygame.Rect((100, 180), entry_size), MANAGER)
password_entry.is_enabled = False
password_entry.set_forbidden_characters([' '])
exit_button = UIButton(pygame.Rect(((WINDOW_SIZE[0] - 300, WINDOW_SIZE[1] - 250), entry_size)), 'Выйти из аккаунта',
                       MANAGER)
# кнопка для изменения пароля/имени V
change_data_button = UIButton(pygame.Rect((150 + password_entry.rect[0], 260), (100, 50)), 'Изменить', MANAGER)
delete_account_button = UIButton(pygame.Rect(((WINDOW_SIZE[0] - 300, WINDOW_SIZE[1] - 150), entry_size)),
                                 'Удалить аккаунт', MANAGER)
cancel_button = UIButton(pygame.Rect((50 + password_entry.rect[0], 270), (100, 35)), 'Отмена', MANAGER, visible=0)
exit_account_txt, delete_account_txt = 'Вы уверены, что хотите выйти из аккаунта?', \
                                       'Вы уверены, что хотите удалить аккаунт?'
exit_account = delete_account = close_game = None
login = password = ''


def change_btn(text, editable, cancel_btn_visitable):
    # меняет параметры виджетов
    change_data_button.set_text(text)
    name_entry.is_enabled = editable
    password_entry.is_enabled = editable
    cancel_button.visible = cancel_btn_visitable


def change_personal_data(old_login, old_password, new_login, new_password):
    from authorise_window import check_login, check_password
    '''обновляет данные'''
    password_exists = cursor.execute('SELECT id FROM Person WHERE password = ? AND id != ?',
                                     (new_password, USER_ID)).fetchmany()
    if check_login(new_login) and check_password(new_password) and not password_exists:
        cursor.execute('UPDATE Person SET name = ?, password = ? WHERE id = ?', (new_login, new_password, USER_ID))
        connect.commit()
        return True
    else:
        name_entry.set_text(old_login)
        password_entry.set_text(old_password)
        if not check_login(new_login):
            error = 'Имя не может быть пустым' if not new_login else 'Имя не может состоять только из пробелов'
            create_confirmation_window('Ошибка имени!', error, MANAGER)
            return
        if password_exists:
            create_confirmation_window('Ошибка пароля!', 'Такой пароль уже существует - придумайте другой', MANAGER)
            return
        if not check_password(new_password):
            password_rules = {"Длина не может быть меньше 8": len(password) < 8, "Добавьте букву": password.isdigit(),
                              "Добавьте цифру": not bool(i for i in password if i.isdigit())}
            error = [key for key in password_rules if password_rules[key]][0]
            create_confirmation_window('Ошибка пароля!', error, MANAGER)
            return
        return


def main(user_id):
    global USER_ID, exit_account, delete_account, close_game, login, password
    USER_ID = user_id
    screen.blit(maze_image, (0, 0))
    pygame.display.set_caption('Личный кабинет')
    time_delta = CLOCK.tick(60) / 1000.0
    login, password = cursor.execute('SELECT name, password FROM Person WHERE id = ?', (USER_ID,)).fetchone()

    name_entry.set_text(login)
    password_entry.set_text(password)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game = create_confirmation_window('Подтвердите действие', exit_game_text,
                                                        MANAGER)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == exit_button:
                    exit_account = create_confirmation_window('Подтвердите действие', exit_account_txt, MANAGER)
                if event.ui_element == delete_account_button:
                    delete_account = create_confirmation_window('Подтвердите действие', delete_account_txt, MANAGER)
                if event.ui_element == cancel_button:
                    name_entry.set_text(login)
                    password_entry.set_text(password)
                    change_btn('Изменить', False, 0)
                if event.ui_element == change_data_button:
                    if change_data_button.text == 'Изменить':
                        change_btn('Сохранить', True, 1)
                    else:
                        change_btn('Изменить', False, 0)
                        new_login, new_password = name_entry.get_text(), password_entry.get_text()
                        if change_personal_data(login, password, new_login, new_password):
                            login, password = new_login, new_password
                            create_confirmation_window('Информация', 'Данные изменены', MANAGER)
                        else:
                            pass

            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                from main_page import main as go_to_main
                if event.ui_element == exit_account:
                    go_to_main(0)
                if event.ui_element == delete_account:
                    cursor.execute('DELETE FROM Person WHERE id = ?', (USER_ID,))
                    connect.commit()
                    go_to_main(0)
                if event.ui_element == close_game:
                    terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if go_back.check_mouse_pos(pygame.mouse.get_pos()):
                    from main_page import main as go_to_main
                    go_to_main(USER_ID)

            MANAGER.process_events(event)
        screen.blit(maze_image, (0, 0))
        go_back.update()
        MANAGER.update(time_delta)
        MANAGER.draw_ui(screen)
        pygame.display.update()


if __name__ == '__main__':
    main(1)
