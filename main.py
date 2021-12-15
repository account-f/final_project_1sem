import arcade
import arcade.gui
import random
import math
import os

# экран:
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Turret"
mouse_x = 0
mouse_y = 0
GROUND = 80  # высота земли

# объекты:
BULLET_SPEED = 48  # полная скорость пули
TANKETTE_VELOCITIES = [2, 1.5, 0, 1]  # полные скорости танкеток (в соответствии с размером)
TANKETTE_HPS = [4, 8, 0, 12]
DRONE_VELOCITY = 2.5  # полная скорость дрона
COPTER_VELOCITY = 3  # полная скорости коптера
COPTER_HPS = [3, 6]
BULLET_PENETRA = 3  # HP пули главной пушки
TOLERANCE = SCREEN_WIDTH / 10

ENEMIES = [0] * 5
ENEMIES[4] = ["tankette"]
ENEMIES[2] = ["tankette", "drone"]
ENEMIES[1] = ["tankette", "copter1", "copter2"]  # list of enemies which cost 1

G_for_money = 1  # gravitational acceleration for money
G_for_bullets = 0.1  # gravitational acceleration for bullets

upgrade_list_1 = [0, 1, 2, 3]

# время:
FPS = 60
FPB = 4  # frames per one texture image of explosion
SPAWN_INTERVAL = FPS*10  # time interval for one spawn cycle


class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class StartButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        global menu
        menu = False
        self.text = 'Resume'


class MyGame(arcade.Window):
    """ Main application class """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        global menu

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.game_over = False
        arcade.set_background_color((255, 255, 255))

        self.frame_count = -1  # счётчик обновлений экрана
        self.score = 0  # счёт
        self.enemy_points = 0  # текущее значение очков врага
        self.spawn_timer = 0  # таймер, по которому рассчитывается спавн врагов
        self.cash = 0  # счётчик валюты
        self.text = "start"
        self.text_time = -1  # timer for text
        self.health_hint_marker = False

        self.icons = None  # иконки
        self.moneys = None  # "монетки", а по сути запчасти, служащие внутриигровой валютой
        self.enemies = None  # все враги
        self.ground_enemies = None  # наземные враги
        self.air_enemies = None  # воздушные враги
        self.enemy_kamikaze = None  # враги-камикадзе: взрываются по достижении цели
        self.bullet_list = None  # список пуль
        self.enemy_bullet_list = None  # список вражеских снарядов
        self.ground_lateral_weapons = None  # второстепенные наземные пушки
        self.static_objects = None  # другие объекты
        self.objects = None  # список для дота
        self.player_guns = None  # наводящиеся пушки игрока
        self.guns = None  # пушки врагов
        self.booms = None  # список действующих анимаций взрывов
        self.spawn_list = []  # list contains name of enemy, size and random time of spawn

        # инициализация звуков
        self.main_sound = arcade.load_sound("sounds/background.m4a", False)
        self.helicopter_crash = arcade.load_sound("sounds/helicopter_crash.mp3", False)
        self.end_of_game = arcade.load_sound("sounds/game_over.wav", False)
        self.laser_sound = arcade.load_sound("sounds/laser.mp3", False)
        self.minigun_sound = arcade.load_sound("sounds/minigun_fire.mp3", False)
        self.heal_sound = arcade.load_sound("sounds/heal.mp3", False)
        self.upgrade_sound = arcade.load_sound("sounds/upgrade.mp3", False)
        self.cannon_sound = arcade.load_sound("sounds/cannon_fire.mp3", False)

        # инициализация фона и установка его координат:
        self.background = arcade.Sprite("pictures/desert.png")  # background picture
        self.background.center_x = SCREEN_WIDTH/2
        self.background.center_y = SCREEN_HEIGHT/2

        self.max_enemy_points = 5  # initial number of enemy points, using to spawn
        self.mouse_pressed_test = False  # variable checks if key button IS pressed

        # настройка предигрового меню:
        menu = True
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout()

        # добавление кнопки старта:
        start_button = StartButton(text='Start', width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        # кнопки выхода:
        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def setup(self):
        """ Set up the game and initialize the variables """
        # фоновый звук:
        arcade.play_sound(self.main_sound, volume=0.2, looping=True)

        # инициализация различных списков:
        self.icons = arcade.SpriteList()
        self.moneys = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.static_objects = arcade.SpriteList()
        self.ground_enemies = arcade.SpriteList()
        self.air_enemies = arcade.SpriteList()
        self.enemy_kamikaze = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.ground_lateral_weapons = arcade.SpriteList()
        self.objects = arcade.SpriteList()
        self.player_guns = arcade.SpriteList()
        self.guns = arcade.SpriteList()
        self.booms = arcade.SpriteList()

        # инициализация главного холма (с записью его расположения на экране и помещением в список objects):
        pillbox = arcade.Sprite("pictures/pillbox.png")
        pillbox.center_x = SCREEN_WIDTH/2
        pillbox.center_y = pillbox.height/2
        pillbox.max_hp = 50
        pillbox.hp = pillbox.max_hp
        self.objects.append(pillbox)

        # инициализация главной пушки (с записью ее расположения на экране и помещением в список player_guns):
        initial_gun = arcade.Sprite("pictures/initial_gun.png")
        initial_gun.center_x = SCREEN_WIDTH/2
        initial_gun.center_y = pillbox.height + 4/9 * initial_gun.width
        initial_gun.damage = 1
        initial_gun.penetra = 1
        initial_gun.fire_type = "ball"
        initial_gun.autofire = False
        initial_gun.rate = 2/FPS  # fire rate: number of created bullets per FPS screen updates
        initial_gun.recharge_time = 0
        self.player_guns.append(initial_gun)

        # инициализация таблицы денег:
        cash_icon = arcade.Sprite("pictures/money_icon.png")
        cash_icon.center_x = SCREEN_WIDTH/2 - 100 - cash_icon.width
        cash_icon.center_y = SCREEN_HEIGHT - 40 + cash_icon.height/2
        self.icons.append(cash_icon)

    def on_draw(self):
        """ Render the screen """

        if menu:
            self.manager.draw()
            return None
        else:
            arcade.start_render()

        # рисование фона и земли:
        self.background.draw()
        arcade.draw_rectangle_filled(SCREEN_WIDTH/2, GROUND/2, SCREEN_WIDTH, 8, (163, 109, 97))
        arcade.draw_rectangle_filled(SCREEN_WIDTH/2, GROUND/4, SCREEN_WIDTH, GROUND/2, (226, 198, 131))

        # рисование различных объектов:
        self.icons.draw()
        self.moneys.draw()
        self.ground_lateral_weapons.draw()
        self.bullet_list.draw()
        self.objects.draw()
        self.static_objects.draw()
        self.enemy_bullet_list.draw()
        self.player_guns.draw()
        self.ground_enemies.draw()
        self.air_enemies.draw()
        self.enemy_kamikaze.draw()
        self.guns.draw()
        self.booms.draw()

        # рисование HP (health points) у наземных врагов и objects:
        for enemy in self.enemies:
            if enemy.hp > 0:
                arcade.draw_text(str(enemy.hp), enemy.center_x - enemy.width/2, enemy.top + 6,
                                 arcade.color.FRENCH_WINE, 16, width=enemy.width, align="center",
                                 font_name="Kenney Future")
        for object in self.objects:
            arcade.draw_text(str(object.hp), object.center_x - object.width/2, object.top + 80,
                             arcade.color.FRENCH_WINE, 25, width=object.width, align="center",
                             font_name="Kenney Future")

        # рисование текста со счётом и монетами:
        arcade.draw_text("SCORE: " + str(self.score), SCREEN_WIDTH/2 + 100, SCREEN_HEIGHT - 40,
                         arcade.color.FRENCH_WINE, 25, font_name="Kenney Future")

        if self.cash < 10:
            arcade.draw_text(str(self.cash), SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT - 40,
                             arcade.color.FRENCH_WINE, 25, font_name="Kenney Future")
        else:
            arcade.draw_text(str(self.cash), SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT - 40,
                             arcade.color.DARK_PASTEL_GREEN, 25, font_name="Kenney Future")

        if self.text_time >= 0:
            arcade.draw_text(self.text, 0, 3 * SCREEN_HEIGHT / 4,
                             arcade.color.WHITE, 25, font_name="Kenney Future",
                             width=SCREEN_WIDTH, align="center")

    def on_update(self, delta_time):
        """ Вся логика игры здесь """
        if not self.game_over and not menu:

            # обновление счетчика кадров и таймера для текста:
            self.frame_count += 1
            self.text_time -= 1

            self.spawn()

            for gun in self.player_guns:
                # обновление угла наклона пушки игрока
                angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)
                gun.angle = math.degrees(angle) - 90
                gun.recharge_time -= 1
                if (gun.autofire and self.mouse_pressed_test) is True:
                    self.player_fire(gun)

            for bullet in self.bullet_list:
                # генерация списка врагов, столкнувшихся с пулей
                hit_list = (arcade.check_for_collision_with_list(bullet, self.enemies))
                for enemy in hit_list:
                    # обновление HP у врагов и пули; ее удаление в случае отсутствия HP:
                    if bullet.hp > 0:
                        enemy.hp -= bullet.damage
                        bullet.hp -= 1
                    else:
                        bullet.remove_from_sprite_lists()

                if (bullet.bottom < GROUND/2 or bullet.top > SCREEN_HEIGHT
                        or bullet.right < 0 or bullet.left > SCREEN_WIDTH
                        or bullet.hp <= 0):
                    # удаление пули при ее покидании экрана и/или отсутствии HP:
                    bullet.remove_from_sprite_lists()
                bullet.change_y -= G_for_bullets

            for enemy in self.ground_enemies:
                enemy.time += 1
                if enemy.hp <= 0:
                    self.generate_money(enemy)
                    if len(self.moneys) >= 10:
                        self.screen_text("DON'T FORGET COLLET DETAILS!")
                    # удаление танкетки при отсутствии у нее HP:
                    enemy.remove_from_sprite_lists()
                    self.score += enemy.size  # начисление очков в зависимости от размера врага
                else:
                    distance = abs(enemy.center_x - SCREEN_WIDTH / 2)

                    # остановка танкетки на определенном расстоянии от холма (в зависимости от размера):
                    if ((enemy.size == 1 and distance < SCREEN_WIDTH/6) or
                            (enemy.size == 2 and distance < SCREEN_WIDTH/5) or
                            (enemy.size == 4 and distance < SCREEN_WIDTH/4)):
                        self.fire(enemy)
                        enemy.change_x = 0

            for enemy in self.air_enemies:
                enemy.gun.angle = math.degrees(math.atan2(enemy.center_y - self.objects[0].center_y,
                                                          enemy.center_x - self.objects[0].center_x)) + 90
                enemy.time += 1
                if enemy.hp <= 0:
                    self.generate_money(enemy)
                    enemy.remove_from_sprite_lists()
                    enemy.gun.remove_from_sprite_lists()
                    self.score += enemy.size  # начисление очков в зависимости от размера врага
                else:
                    if enemy.time % 2 == 0:
                        self.next_frame(enemy, frames=6)
                    if enemy.type == 2 and enemy.time >= FPS:
                        self.fire(enemy.gun)
                    if ((enemy.center_x - self.objects[0].center_x) ** 2 +
                            (enemy.center_y - self.objects[0].center_y) ** 2
                            <= (SCREEN_HEIGHT / 3) ** 2):
                        enemy.change_x = 0
                        enemy.change_y = 0
                        enemy.gun.change_x = 0
                        enemy.gun.change_y = 0
                        self.fire(enemy.gun)

                if (enemy.center_x < 0 or enemy.center_x > SCREEN_WIDTH or
                        enemy.center_y < 0 or enemy.center_y > SCREEN_HEIGHT):
                    enemy.recharge_time = 10  # enemy.recharge_time can't reach 0 if enemy isn't on screen
                if (enemy.center_x < - TOLERANCE or enemy.center_x > SCREEN_WIDTH + TOLERANCE or
                        enemy.center_y < - TOLERANCE or enemy.center_y > SCREEN_HEIGHT + TOLERANCE):
                    enemy.remove_from_sprite_lists()
                    if hasattr("enemy", "gun") is True:
                        enemy.gun.remove_from_sprite_lists()

            for enemy in self.enemy_kamikaze:
                if enemy.hp <= 0:
                    # удаление дрона с созданием на его месте взрыва:
                    self.create_boom(enemy.center_x, enemy.center_y, enemy.change_x, enemy.change_y)
                    enemy.remove_from_sprite_lists()
                    self.score += enemy.size  # начисление очков в зависимости от размера врага

                    # включение звука взрыва:
                    arcade.play_sound(self.helicopter_crash, volume=0.3)
                else:
                    # проверка удара дроном по игроку с изменением HP игрока и занулением HP дрона:
                    hit_list = arcade.check_for_collision_with_list(enemy, self.objects)
                    for object in hit_list:
                        object.hp -= 10

                        self.create_boom(enemy.center_x, enemy.center_y, enemy.change_x, enemy.change_y)
                        enemy.remove_from_sprite_lists()
                        arcade.play_sound(self.helicopter_crash, volume=0.3)

            for boom in self.booms:
                # анимация взрыва:
                boom.count += 1
                if boom.count % FPB == 0:
                    # updates every FPB frames
                    file = "pictures/boom" + str(boom.count // FPB) + ".png"
                    if os.path.exists(file):
                        # file named as boom1, boom2 etc; this checks existing in agreement with boom.count
                        boom.texture = arcade.load_texture(file)
                    else:
                        boom.remove_from_sprite_lists()

            for object in self.objects:
                # обновление HP игрока и замена текстуры холма при его занулении:
                hit_list = arcade.check_for_collision_with_list(object, self.enemy_bullet_list)
                for bullet in hit_list:
                    object.hp -= bullet.size

                    bullet.remove_from_sprite_lists()

                if object.hp <= 0:
                    # замена картинки холма при достижении нулевого HP игроком:
                    object.texture = arcade.load_texture("pictures/pillbox_destructed.png")
                    object.hp = 0
                    arcade.play_sound(self.end_of_game, volume=0.7)
                    self.game_over = True
                    print("Your score: ", self.score)

            # money rules (movement and scoring system):
            for money in self.moneys:
                if money.caught_up is False:
                    money.change_y -= G_for_money
                if money.bottom <= GROUND/2 + 4:
                    money.change_x = 0
                    money.change_y = 0
                if math.dist([mouse_x, mouse_y], [money.center_x, money.center_y]) <= 20:
                    # picking up money with the mouse:
                    angle = math.atan2(self.icons[0].center_y - money.center_y, self.icons[0].center_x - money.center_x)
                    money.change_x = math.cos(angle) * 32
                    money.change_y = math.sin(angle) * 32
                    money.caught_up = True
                if math.dist([self.icons[0].center_x, self.icons[0].center_y], [money.center_x, money.center_y]) <= 20:
                    # adding to the cash & main score with the money having approached the cash icon:
                    self.cash += 1
                    self.score += 1
                    if self.cash >= 10 and self.health_hint_marker is False:
                        self.screen_text("PRESS H TO HEAL FOR 10 DETAILS")
                        self.health_hint_marker = True
                    money.remove_from_sprite_lists()

            for gun in self.ground_lateral_weapons:
                if len(self.ground_enemies) > 0:
                    self.horizontal_lateral_weapons_fire(gun)

            if (self.frame_count + 2) % (SPAWN_INTERVAL) == 0:
                self.upgrade()

            # bullet movement:
            for bullet in self.enemy_bullet_list:
                if (bullet.bottom < GROUND/2 or bullet.top > SCREEN_HEIGHT
                        or bullet.right < 0 or bullet.left > SCREEN_WIDTH):
                    bullet.remove_from_sprite_lists()
                bullet.change_y -= G_for_bullets  # bullet velocity change caused by gravity

            # обновление объектов игры:
            self.moneys.update()
            self.enemies.update()
            self.bullet_list.update()
            self.enemy_bullet_list.update()
            self.enemy_kamikaze.update()
            self.static_objects.update()
            self.booms.update()
            self.guns.update()
            self.air_enemies.update_animation(1)

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """ Считывание расположения мыши игрока и изменение соответсвующих глобальных переменных """
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        """ Вызывается при нажатии мыши игроком """
        self.mouse_pressed_test = True
        if self.game_over is False:
            for gun in self.player_guns:
                self.player_fire(gun)

    def on_mouse_release(self, x, y, button, modifiers):
        """ Вызывается при отпускании мыши игроком """
        self.mouse_pressed_test = False

    def on_key_press(self, symbol, modifiers):
        """ Вызывается при нажатии кнопки клавиатуры """
        if symbol == arcade.key.KEY_1:
            self.player_guns[0].texture = arcade.load_texture("pictures/gun.png")
            self.player_guns[0].fire_type = "laser"
            self.player_guns[0].damage = 2
            self.player_guns[0].penetra = 3
            self.player_guns[0].autofire = False
            self.player_guns[0].rate = 2/FPS  # fire rate: number of created bullets per FPS screen updates
        if symbol == arcade.key.KEY_2:
            self.player_guns[0].texture = arcade.load_texture("pictures/machine_gun.png")
            self.player_guns[0].fire_type = "high_velocity_bullet"
            self.player_guns[0].damage = 1
            self.player_guns[0].penetra = 1
            self.player_guns[0].autofire = True
            self.player_guns[0].rate = 10/FPS
        if symbol == arcade.key.H:
            self.heal(10)

    def fire(self, enemy):
        """
        Makes enemy firing: creates bullets if enemy is aimed and keep aiming if not
        :param enemy: firing enemy
        """
        if enemy.recharge_time == 0:  # проверка счетчика времени перезарядки
            delta_angle = random.randint(-20, 20)  # разброс выстрела

            bullet = arcade.Sprite("pictures/" + str(enemy.size) + "_bullet.png", 1)
            bullet.size = enemy.size
            bullet.center_x = enemy.center_x
            bullet.center_y = enemy.center_y
            angle = math.atan2(enemy.center_y - self.objects[0].center_y,
                               enemy.center_x - self.objects[0].center_x) + delta_angle * math.pi / 180
            bullet.angle = math.degrees(angle)
            bullet.change_x = - math.cos(angle) * BULLET_SPEED
            bullet.change_y = - math.sin(angle) * BULLET_SPEED
            if enemy.size == 1:
                enemy.recharge_time = 30
            elif enemy.size == 2:
                enemy.recharge_time = 50
            elif enemy.size == 4:
                enemy.recharge_time = 75
            self.enemy_bullet_list.append(bullet)
        else:
            enemy.recharge_time -= 1

    def player_fire(self, gun):
        """
        Осуществляет огонь и перезарядку со стороны игрока
        :param gun: какая пушка стреляет
        """
        global bullet
        if gun.recharge_time <= 0:
            # создание пули и помещение ее в список пуль игрока:
            angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)
            if gun.fire_type == "laser":
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
                arcade.play_sound(self.laser_sound, volume=2)
                bullet.change_x = math.cos(angle) * BULLET_SPEED
                bullet.change_y = math.sin(angle) * BULLET_SPEED
            elif gun.fire_type == "high_velocity_bullet":
                bullet = arcade.Sprite("pictures/high_velocity_bullet.png")
                bullet.change_x = math.cos(angle) * 128
                bullet.change_y = math.sin(angle) * 128
                arcade.play_sound(self.minigun_sound, volume=0.1)
            elif gun.fire_type == "ball":
                bullet = arcade.Sprite("pictures/2_bullet.png")
                bullet.change_x = math.cos(angle) * BULLET_SPEED
                bullet.change_y = math.sin(angle) * BULLET_SPEED
                arcade.play_sound(self.cannon_sound, volume=0.1)
            elif gun.fire_type == "ball2":
                bullet = arcade.Sprite("pictures/4_bullet.png")
                bullet.change_x = math.cos(angle) * BULLET_SPEED
                bullet.change_y = math.sin(angle) * BULLET_SPEED
                arcade.play_sound(self.cannon_sound, volume=0.1)

            # setting up other bullet's parameters:
            bullet.hp = gun.penetra
            bullet.damage = gun.damage
            bullet.angle = math.degrees(angle)
            bullet.center_x = gun.center_x + math.cos(angle) * bullet.width/4
            bullet.center_y = gun.center_y + math.sin(angle) * bullet.width/4

            self.bullet_list.append(bullet)

            gun.recharge_time = 1/gun.rate

    def horizontal_lateral_weapons_fire(self, weapon, double=True):
        """
        Makes ground lateral weapon firing.
        :param weapon: firing weapon:
        :param double: if weapon id double and can fire in two sides
        """
        if weapon.recharge_time == 0:
            if double is True:
                for direct in [-1, 1]:
                        bullet = arcade.Sprite("pictures/4_bullet.png")
                        bullet.center_x = weapon.center_x
                        bullet.center_y = weapon.center_y
                        bullet.change_x = 32 * direct
                        bullet.hp = 1
                        bullet.damage = 2
                        self.bullet_list.append(bullet)
            weapon.recharge_time = 1/weapon.rate
        else:
            weapon.recharge_time -= 1

    def create_boom(self, x, y, Vx, Vy):
        """
        Creates an explosion. boom.count helps for switching frames
        :param x: x coordinate of center
        :param y: y coordinate of center
        :param Vx: velocity projection on the x-axis
        :param Vy: velocity projection on the y-axis
        """
        boom = arcade.Sprite("pictures/boom1.png")
        boom.center_x = x + Vx
        boom.center_y = y + Vy
        boom.change_x = Vx/2  # keeps moving
        boom.change_y = Vy/2 - 1  # and slowly falls down
        boom.count = FPB
        self.booms.append(boom)

    def default_tankette_spawn(self, size, recharge_time=0):
        """
        Creates a tankette
        :param size: size using for creating bullets
        :param recharge_time: initial recharge time
        """
        direct = random.choice([1, -1])
        file = "pictures/" + str(size) + "_tankette 0 .png"
        tankette = arcade.Sprite(file, flipped_horizontally=bool(abs(direct-1)/2))
        tankette.file = file
        tankette.size = size
        tankette.direct = direct
        tankette.time = 0  # initial existing time
        tankette.change_x = direct * TANKETTE_VELOCITIES[size - 1]
        tankette.center_x = SCREEN_WIDTH/2 - direct * (SCREEN_WIDTH/2 + tankette.width)
        tankette.bottom = GROUND/2
        tankette.hp = TANKETTE_HPS[size - 1]  # установление HP танкетки согласно ее размеру
        tankette.recharge_time = recharge_time
        tankette.frame = 0
        self.ground_enemies.append(tankette)
        self.enemies.append(tankette)

    def default_drone_spawn(self, size):
        """
        Creates a drone
        :param size: size
        """
        direct = random.choice([1, -1])
        drone = arcade.Sprite("pictures/drone.png")
        drone.size = size
        drone.center_x = SCREEN_WIDTH/2 - direct * (SCREEN_WIDTH/2 + drone.width)
        drone.top = random.randint(SCREEN_HEIGHT//2, SCREEN_HEIGHT)
        angle = math.atan2(drone.center_y - self.objects[0].center_y, drone.center_x - self.objects[0].center_x)
        drone.change_x = - DRONE_VELOCITY * math.cos(angle)
        drone.change_y = - DRONE_VELOCITY * math.sin(angle)
        drone.hp = 1

        # добавление дрона к соответствующим спискам врагов:
        self.enemy_kamikaze.append(drone)
        self.enemies.append(drone)

    def default_copter1_spawn(self, size):
        """
        Creates a (heli)copter
        :param size: size
        helicopter, helicopter
        """
        direct = random.choice([1, -1])
        file = "pictures/" + str(size) + "_copter 0 .png"
        copter = arcade.Sprite(file)
        copter.type = 1
        copter.center_x = SCREEN_WIDTH/2 - direct * (SCREEN_WIDTH/2 + copter.width)
        copter.top = random.randint(SCREEN_HEIGHT//2, SCREEN_HEIGHT)
        copter.direct = direct
        copter.file = file
        copter.size = size
        copter.hp = COPTER_HPS[size - 1]
        copter.time = 0  # initial existing time

        angle = math.atan2(self.objects[0].center_y - copter.center_y,
                           self.objects[0].center_x - copter.center_x)

        copter.change_x = COPTER_VELOCITY * math.cos(angle)
        copter.change_y = COPTER_VELOCITY * math.sin(angle)

        copter.gun = arcade.Sprite("pictures/gun1.png")
        copter.gun.size = 1
        copter.gun.angle = math.degrees(angle) - 90
        copter.gun.center_x = copter.center_x
        copter.gun.top = copter.center_y + 8
        copter.gun.recharge_time = 0
        copter.gun.change_x = copter.change_x
        copter.gun.change_y = copter.change_y

        self.air_enemies.append(copter)
        self.enemies.append(copter)
        self.guns.append(copter.gun)

    def default_copter2_spawn(self, size):
        """
        Creates a (heli)copter using same function for other type.
        Changes variables using sprite lists.
        :param size: size
        helicopter, helicopter
        """
        self.default_copter1_spawn(size)

        self.air_enemies[-1].change_x = COPTER_VELOCITY * self.air_enemies[-1].direct
        self.air_enemies[-1].change_y = 0

        self.air_enemies[-1].gun.change_x = self.air_enemies[-1].change_x
        self.air_enemies[-1].gun.change_y = self.air_enemies[-1].change_y
        self.air_enemies[-1].type = 2

    def next_frame(self, object, frames=2):
        """
        Анимирует объект путем регулярной замены его текстуры.
        Takes info about current frame from filename.
        Changes texture by changing number of frame in filename.
        :param object: animating object
        :param frames: number of frames of animation
        """
        number = int(object.file.split(" ")[1])
        if number + 1 == frames:
            number = -1
        object.file = object.file.split(" ")[0] + " " + str((number + 1) % frames) + " " + object.file.split(" ")[2]
        object.texture = arcade.load_texture(object.file, flipped_horizontally=bool(abs(object.direct-1)/2))

    def spawn(self):
        """
        Increases the level of difficulty. Spawns enemies depending on the enemy_points
        Big tankette "costs" 4 points, so game can generate it from 0 to 5, if enemy_points=20.
        Next it generates enemies which costs 2 points using remained points.
        If after all spawn there are points left, it goes to the next cycle.
        Creates list of enemies which spawn at this cycle.
        """
        if self.spawn_timer == 0:
            self.spawn_list = []

            numbers = [0] * 5
            self.enemy_points += self.max_enemy_points
            numbers[1] = random.randint(0, self.enemy_points // (1*2))
            self.enemy_points -= numbers[1]
            numbers[4] = random.randint(0, self.enemy_points // (4*2))
            self.enemy_points -= numbers[4] * 4
            numbers[2] = self.enemy_points // 2
            self.enemy_points -= numbers[2] * 2

            for size in (1, 2, 4):
                # фиксируем размер
                for elem in ENEMIES[size]:
                    # фиксируем тип врага фиксированного размера
                    current_number = random.randint(0, 3 * numbers[size] // 4)
                    for _ in range(current_number):
                        self.spawn_list.append([elem, size, random.randint(1, SPAWN_INTERVAL-1)])
                    numbers[size] -= current_number
                if numbers[size] > 0:
                    self.spawn_list.append([ENEMIES[size][len(ENEMIES[size]) - 1],
                                            size, random.randint(0, SPAWN_INTERVAL)])
            self.spawn_timer = SPAWN_INTERVAL
            self.max_enemy_points += 3
        else:
            self.spawn_timer -= 1
            for enemy_str in self.spawn_list:
                if self.spawn_timer == enemy_str[2]:
                    eval("self.default_" + str(enemy_str[0]) + "_spawn(" + str(enemy_str[1]) + ")")

    def generate_money(self, enemy):
        for _ in range(random.randint(0, enemy.size)):
            money = arcade.Sprite("pictures/money" + str(random.randint(1, 10)) + ".png")
            money.center_x = enemy.center_x
            money.center_y = enemy.center_y
            money.change_x = random.randint(-3, 3)
            money.change_y = random.randint(-5, 5)
            money.caught_up = False
            self.moneys.append(money)

    def heal(self, hp):
        if self.objects[0].hp + hp <= self.objects[0].max_hp and self.cash >= hp and not self.game_over:
            self.objects[0].hp += hp
            self.cash -= hp
            arcade.play_sound(self.heal_sound, volume=1)

    def upgrade(self):
        # обновление (согласно уровням) и вывод сопутствующего сообщения на экране:
        if len(upgrade_list_1) > 0:
            upgrade = random.choice(upgrade_list_1)
            upgrade_list_1.remove(upgrade)
            arcade.play_sound(self.upgrade_sound, volume=1)
            if upgrade == 0:
                lateral_weapons = arcade.Sprite("pictures/lateral_weapons.png")
                lateral_weapons.center_x = self.objects[0].center_x
                lateral_weapons.center_y = GROUND/2 + 32
                lateral_weapons.rate = 1/FPS
                lateral_weapons.recharge_time = 30
                self.ground_lateral_weapons.append(lateral_weapons)
                self.screen_text("WEAPONS UPGRADED!")
            elif upgrade == 1:
                shield = arcade.Sprite("pictures/shield.png")
                shield.center_x = self.objects[0].center_x
                shield.bottom = self.objects[0].bottom
                self.static_objects.append(shield)
                self.objects[0].max_hp += 25
                self.objects[0].hp += 25
                self.screen_text("SHIELD ADDED! +25HP")
            elif upgrade == 2:
                self.player_guns[0].texture = arcade.load_texture("pictures/initial_gun_upgraded.png")
                self.player_guns[0].damage *= 2
                self.player_guns[0].fire_type = "ball2"
                self.screen_text("GUN UPGRADED! DAMAGE IMPROVED")
            elif upgrade == 3:
                self.player_guns[0].autofire = True
                self.screen_text("GUN UPGRADED! AUTOFIRE MODE UNLOCKED:\nHOLD MOUSE BUTTON FOR FIRE")

    def screen_text(self, text):
        """
        Печать текста на экране
        :param text: text printing on the screen
        """
        self.text = text
        self.text_time = FPS*3


def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
