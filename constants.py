# экран:
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Turret"
mouse_x = 0
mouse_y = 0
GROUND = 80  # высота земли
menu = True
started = False

# объекты:
BULLET_SPEED = 48  # полная скорость пули
TANKETTE_VELOCITIES = [2, 1.5, 0, 1]  # полные скорости танкеток (в соответствии с размером)
TANKETTE_HPS = [4, 8, 0, 12]  # жизни танкеток
DRONE_VELOCITY = 2.5  # полная скорость дрона
COPTER_VELOCITY = 3  # полная скорости коптера
COPTER_HPS = [3, 6]  # жизни дронов
BULLET_PENETRA = 3  # HP пули главной пушки
TOLERANCE = SCREEN_WIDTH / 10  # величина отклонения, использующаяся для корректной вражеской атаки

ENEMIES = [0] * 5
ENEMIES[4] = ["tankette"]  # список врагов 'стоимостью' и размера 4
ENEMIES[2] = ["tankette", "drone"]  # список врагов 'стоимостью' и размера 2
ENEMIES[1] = ["tankette", "copter1", "copter2"]  # список врагов 'стоимостью' и размера 1

G_for_money = 1  # ускорение свободного падения для деталек
G_for_bullets = 0.1  # ускорение свободного падения для пуль

upgrade_list_1 = [0, 1, 2, 3]

# время:
FPS = 60
FPB = 4  # переменная, устанавливающая частоту смену кадров анимации взрыва
SPAWN_INTERVAL = FPS*10  # интервал времени, отводящийся на один цикл 'спавна'