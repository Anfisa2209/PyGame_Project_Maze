class Creature():

    def __init__(self, type):
        super.__init__(type)
        self.health = type
        self.speed = 2
        #Параметры здоровья, и скорости

    def get_pos(self):
        pass
        # В этой функции берём позицию существа и пихаем в кортеж

    def do_die(self):
        pass
    # В этой функции существо умирает и удаляестя с поля(опционально - анимация смерти)

    def get_hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.do_die()
        #Получение урона, если хп меньше либо равно нулю, то смерть

    def move(self, direction):
        x, y = self.get_pos()
        if direction == 'up':
            y -= self.speed
        elif direction == 'down':
            y += self.speed
        if direction == 'left':
            y -= self.speed
        elif direction == 'right':
            y += self.speed
    # Собственно, движение


class Enemy(Creature):

    def get_path(self):
        pass
        # Здесь волновым алгоритмом определяем, как легче пройти к игроку и разворачиваемся в ту сторону и записываем в переменную direction. 'up', 'down', 'left', 'right' - наброски, их можно менять
    def check_can_attack(self):
        pass
        #Тут проверяем, можем ли атаковать
    def do_attack(self):
        pass
    #Атака

class Player(Creature):
    def do_attack(self):
        pass
    #Атака

    def take_weapon(self):
        pass
    #Берём оружие
