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
            x -= self.speed
        elif direction == 'right':
            x += self.speed
    # Собственно, движение


class Enemy(Creature):
    def appera(self, pos):
        pass

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
    def __init__(self, type):
        super().__init__(type)
        self.health = type
        self.speed = 2
        self.first_weapons = 0
        self.second_weapons = 0
        self.third_weapons = 0
        self.current_weapon = 1
        self.direction = 1
        self.attacking_weapons = []

    def set_current(self, type):
        self.current_weapon = type
    #Меняем оружие

    def do_attack(self):
        self.attacking_weapons.append(Weapon(flying=True, type=self.current_weapon, direction=self.direction))
    #Атака

    def take_weapon(self):
        pass
    #Берём оружие

    def take_cherry(self):
        if self.health < 10:
            self.health += 1
        else:
            pass
    #берём вишенку
    def interaction(self):
        pass
    #взаимодействие

class Weapon():
    def __init__(self, type, direction, flying):
        self.type = type
        self.damage = type
        self.range = type
        self.direction = direction
        self.flying = flying
        self.visible = True
        self.cells_to_fly = type

    def do_fly(self, direction):
        pass

    def check_hit_enemy(self):
        pass

    def check_hit_wall(self):
        pass

    def appear(self, pos):
        pass