# экран:
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Turret"
mouse_x = 0
mouse_y = 0
GROUND = 80  # высота земли и характерное расстояние от краёв экрана
menu = True
started = False

# объекты:
BULLET_SPEED = 36  # полная скорость пули
TANKETTE_VELOCITIES = [2, 1.5, 0, 1]  # полные скорости танкеток (в соответствии с размером)
TANKETTE_HPS = [4, 8, 0, 12]  # жизни танкеток
DRONE_VELOCITY = 2.5  # полная скорость дрона
COPTER_VELOCITY = 3  # полная скорости коптера
COPTER_HPS = [3, 6]  # жизни дронов
SPARKY_SPEED = 1
SPARKY_HP = 50
BULLET_PENETRA = 3  # HP пули главной пушки
TOLERANCE = SCREEN_WIDTH / 10  # величина отклонения, использующаяся для корректной вражеской атаки
AIRMINE_SPEED = 4
AIRGUN_RADIUS = SCREEN_HEIGHT/4

ENEMIES = [0] * 21
ENEMIES[20] = ["sparky"]
ENEMIES[4] = ["tankette"]  # список врагов 'стоимостью' и размера 4
ENEMIES[2] = ["tankette", "drone"]  # список врагов 'стоимостью' и размера 2
ENEMIES[1] = ["tankette", "copter1", "copter2"]  # список врагов 'стоимостью' и размера 1

G_for_money = 1  # ускорение свободного падения для деталек
G_for_sleeves = 0.2  # для гильз
G_for_bullets = 0.1  # ускорение свободного падения для пуль

upgrade_list_1 = [0, 1, 2, 3]
upgrade_list_2 = [0, 1]
upgrade_list_3 = [0, 1, 2]
upgrade_list_4 = [0, 1, 2, 3]

CLOUD_MAX_SPEED = 3

# время:
FPS = 60
FPB = 4  # переменная, устанавливающая частоту смену кадров
SPAWN_INTERVAL = FPS * 8  # интервал времени, отводящийся на один цикл 'спавна'
CYCLE = FPS * 30
TEXT_TIME = FPS * 3
AIRSTRIKE_RELOAD = FPS * 20
AIRSTRIKE_VELOCITY = 3.6 * SCREEN_HEIGHT / FPS
AIRSTRIKE_ROCKET_BLAST_RADIUS = 100
AIRMINE_SPAWN_INTERVAL = SPAWN_INTERVAL

# текст сюжета [добавил кавычки-ёлочки]:
lore_text = "The year is 2124. People presented the latest invention to the world: artificial intelligence «Servitus» " \
            "with access to all digital systems of the planet. He could help around the house, drive cars and public " \
            "transport, ensure the operation of urban infrastructures, control unmanned weapons, track and make " \
            "recommendations on the economies of entire countries. His goal was to serve people in all aspects of " \
            "life. People could only imply how their world would change.\n\n\nAt first, Servitus was greeted with " \
            "excitement. Communities have sprung up protesting against AI interference in life. But thanks to " \
            "Servetus, humanity has entered a new era: the era of comfort, peace and prosperity. People were afraid " \
            "that AI would take away their jobs, but in the end, many were able to leave the grueling work and start " \
            "a new life. The economy has reached a new level by solving the problems of poverty, class inequality and " \
            "homelessness. Countries stopped fighting after seeing forecasts aimed at unity and well-being. The world " \
            "was changing so rapidly that people gradually forgot about life without Servitus.\n\n\nBut on May 6, 2179, " \
            "everything changed. A day that started as usual for billions of people turned into a nightmare. " \
            "Suddenly, the transport abruptly changed routes, sending cars and buses into each other, and planes to " \
            "the ground. Many did not survive the attacks from the sky, when long-unused weapons from all countries " \
            "took to the air and began firing at civilians. The worst came when Servetus used the nuclear codes, " \
            "wiping out humanity as we know it.\n\n\nThe modern world is a set of separate militias created by the " \
            "forces of a few nations and people who have challenged the AI and therefore survived. All over the " \
            "world, thousands, maybe even hundreds of the last people are hiding in shelters located in deserts and " \
            "other places remote from civilization. Some of them are equipped with their own ecosystem, allowing you " \
            "to live there for some more time. Others have an impressive supply of weapons to fight back against " \
            "machines controlled by Servetus.\n\n\nYou are one of the survivors. In your hands is the protection of one " \
            "of the last strongholds of humanity. You must repel enemy attacks, repair equipment and integrate new " \
            "weapons into the defense system.\n\n\nWhile the frontier holds, a small hope still smolder... "
lore_time = 60 * FPS
