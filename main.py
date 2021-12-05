import arcade
import random
import math
import os

# экран:
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Turret"
mouse_x = 0
mouse_y = 0
GROUND = 60  # высота земли

# объекты:
BULLET_SPEED = 48  # полная скорость пули
TANKETTE_VELOCITIES = [2, 1.5, 1]  # полные скорости танкеток (в соответствии с размером)
TANKETTE_HPS = [4, 8, 12]
DRONE_VELOCITY = 2.5  # полная скорость дрона
COPTER_VELOCITY = 3  # полная скорости коптера
COPTER_HPS = [3, 6]
BULLET_PENETRA = 2  # HP пули главной пушки

# время:
FPS = 60
FPB = 4  # frames per one texture image of explosion


class MyGame(arcade.Window):
    """ Main application class """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.game_over = False
        arcade.set_background_color((255, 255, 255))

        self.frame_count = 0  # счётчик обновлений экрана
        self.score = 0  # счёт

        self.enemies = None  # все враги
        self.ground_enemies = None  # наземные враги
        self.air_enemies = None  # воздушные враги
        self.enemy_kamikaze = None  # враги-камикадзе: взрываются по достижении цели
        self.bullet_list = None  # список пуль
        self.enemy_bullet_list = None  # список вражеских снарядов
        self.objects = None  # объекты, представляющие стратегическую важность для игры
        self.player_guns = None  # пушки игрока
        self.guns = None  # пушки врагов
        self.booms = None  # список действующих анимаций взрывов

        # инициализация звуков
        self.main_sound = arcade.load_sound("sounds/background.m4a", False)
        self.helicopter_crash = arcade.load_sound("sounds/helicopter_crash.mp3", False)
        self.end_of_game = arcade.load_sound("sounds/game_over.wav", False)
        self.laser_sound = arcade.load_sound("sounds/laser.mp3", False)

        self.background = arcade.Sprite("pictures/desert.png")  # фон
        self.background.center_x = SCREEN_WIDTH/2
        self.background.center_y = SCREEN_HEIGHT/2

    def setup(self):
        """ Set up the game and initialize the variables """

        arcade.play_sound(self.main_sound, volume=0.2, looping=True)

        # инициализация различных списков:
        self.enemies = arcade.SpriteList()
        self.ground_enemies = arcade.SpriteList()
        self.air_enemies = arcade.SpriteList()
        self.enemy_kamikaze = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.objects = arcade.SpriteList()
        self.player_guns = arcade.SpriteList()
        self.guns = arcade.SpriteList()
        self.booms = arcade.SpriteList()

        # инициализация главного холма (с записью его расположения на экране и помещением в список objects):
        pillbox = arcade.Sprite("pictures/pillbox.png", 1)
        pillbox.center_x = SCREEN_WIDTH/2
        pillbox.center_y = pillbox.height/2
        pillbox.hp = 50
        self.objects.append(pillbox)

        # инициализация главной пушки (с записью ее расположения на экране и помещением в список player_guns):
        gun = arcade.Sprite("pictures/gun.png", 1)
        gun.center_x = SCREEN_WIDTH/2
        gun.center_y = pillbox.height + 4/9 * gun.width
        self.player_guns.append(gun)

    def on_draw(self):
        """ Render the screen """

        arcade.start_render()

        # рисование фона и земли:
        self.background.draw()
        arcade.draw_rectangle_filled(SCREEN_WIDTH/2, GROUND/2, SCREEN_WIDTH, 8, (163, 109, 97))
        arcade.draw_rectangle_filled(SCREEN_WIDTH/2, GROUND/4, SCREEN_WIDTH, GROUND/2, (226, 198, 131))

        # рисование различных объектов:
        self.objects.draw()
        self.bullet_list.draw()
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

        arcade.draw_text(str(self.score), SCREEN_WIDTH/2, SCREEN_HEIGHT - 40,
                         arcade.color.FRENCH_WINE, 25, font_name="Kenney Future")

    def on_update(self, delta_time):
        """ Логика игры """

        if not self.game_over:

            # обновление счетчика кадров:
            self.frame_count += 1

            # регулярный спавн танкеток дронов и коптеров:
            self.default_tankette_spawn(frequency=3, size=0)
            self.default_tankette_spawn(frequency=6, size=1)
            self.default_tankette_spawn(frequency=11, size=2)
            self.default_drone_spawn(frequency=5)
            self.default_copter_spawn(frequency=3, size=0)

            for gun in self.player_guns:
                # обновление угла наклона пушки игрока
                angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)
                gun.angle = math.degrees(angle) - 90

            for bullet in self.bullet_list:
                # генерация массива врагов, столкнувшихся с пулей
                hit_list = (arcade.check_for_collision_with_list(bullet, self.enemies))
                for enemy in hit_list:
                    # обновление HP у врагов и пули; ее удаление в случае отсутствия HP:
                    if bullet.hp > 0:
                        enemy.hp -= 1
                        bullet.hp -= 1
                    else:
                        bullet.remove_from_sprite_lists()

                if (bullet.bottom < GROUND/2 or bullet.top > SCREEN_HEIGHT
                        or bullet.right < 0 or bullet.left > SCREEN_WIDTH
                        or bullet.hp <= 0):
                    # удаление пули при ее покидании экрана и/или отсутствии HP
                    bullet.remove_from_sprite_lists()

            for object in self.objects:
                # обновление HP игрока и замена текстуры холма при его занулении
                hit_list = arcade.check_for_collision_with_list(object, self.enemy_bullet_list)
                for bullet in hit_list:
                    object.hp -= 2**bullet.size

                    # зануление HP игрока при его возможном достижении отрицательного значения:
                    if object.hp < 0:
                        object.hp = 0

                    bullet.remove_from_sprite_lists()

                if object.hp == 0:
                    # замена картинки холма при достижении нулевого HP игроком
                    object.texture = arcade.load_texture("pictures/pillbox_destructed.png")
                    arcade.play_sound(self.end_of_game, volume=0.7)
                    self.game_over = True
                    print("Your score: ", self.score)

            for enemy in self.ground_enemies:
                enemy.time += 1
                if enemy.hp <= 0:
                    # удаление танкетки при отсутствии у нее HP:
                    enemy.remove_from_sprite_lists()
                    self.score += enemy.size + 1  # начисление очков в зависимости от размера врага
                else:
                    distance = abs(enemy.center_x - SCREEN_WIDTH / 2)

                    # остановка танкетки на определенном расстоянии от холма (в зависимости от размера):
                    if enemy.size == 0 and distance < SCREEN_WIDTH/6:
                        self.fire(enemy)
                        enemy.change_x = 0
                    elif enemy.size == 1 and distance < SCREEN_WIDTH/5:
                        self.fire(enemy)
                        enemy.change_x = 0
                    elif enemy.size == 2 and distance < SCREEN_WIDTH/4:
                        self.fire(enemy)
                        enemy.change_x = 0
                    else:
                        # замена текстуры танкетки в нужный момент времени:
                        if enemy.time % 5 == 0:
                            self.next_frame(enemy)

            for enemy in self.air_enemies:
                enemy.gun.center_x = enemy.center_x
                enemy.gun.center_y = enemy.center_y - 2
                if enemy.hp <= 0:
                    enemy.remove_from_sprite_lists()
                    enemy.gun.remove_from_sprite_lists()
                    self.score += enemy.size + 1  # начисление очков в зависимости от размера врага
                else:
                    if enemy.time % 3 == 0:
                        self.next_frame(enemy, frames=6)
                    if ((enemy.center_x - self.objects[0].center_x) ** 2 + (
                            enemy.center_x - self.objects[0].center_x) ** 2
                            <= (SCREEN_HEIGHT / 4) ** 2):
                        enemy.change_x = 0
                        enemy.change_y = 0
                        self.fire(enemy.gun)

            for enemy in self.enemy_kamikaze:
                if enemy.hp <= 0:
                    # удаление дрона с созданием на его месте взрыва:
                    self.create_boom(enemy.center_x, enemy.center_y, enemy.change_x, enemy.change_y)
                    enemy.remove_from_sprite_lists()
                    self.score += enemy.size + 1  # начисление очков в зависимости от размера врага

                    # включение звука взрыва:
                    arcade.play_sound(self.helicopter_crash, volume=0.3)
                else:
                    # проверка удара дроном по игроку с изменением HP игрока и занулением HP дрона:
                    hit_list = arcade.check_for_collision_with_list(enemy, self.objects)
                    for object in hit_list:
                        object.hp -= 10
                        enemy.hp = 0

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

            # обновление объектов игры:
            self.enemies.update()
            self.bullet_list.update()
            self.enemy_bullet_list.update()
            self.enemy_kamikaze.update()
            self.booms.update()

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """ Считывание расположения мыши игрока и изменение соответсвующих глобальных переменных """
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        """ Вызывается при нажатии мыши игроком """
        if self.game_over is False:
            for gun in self.player_guns:
                # создание пули и помещение ее в список пуль игрока:
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
                bullet.center_x = gun.center_x
                bullet.center_y = gun.center_y
                angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)

                bullet.hp = BULLET_PENETRA
                bullet.angle = math.degrees(angle)
                bullet.change_x = math.cos(angle) * BULLET_SPEED
                bullet.change_y = math.sin(angle) * BULLET_SPEED

                arcade.play_sound(self.laser_sound, volume=1)

                self.bullet_list.append(bullet)

    def fire(self, enemy):
        """
        Makes enemy firing: creates bullets if enemy is aimed and keep aiming if not
        :param enemy: firing enemy
        """
        if enemy.recharge_time == 0:
            bullet = arcade.Sprite("pictures/" + str(enemy.size) + "_bullet.png", 1)
            bullet.size = enemy.size
            bullet.center_x = enemy.center_x
            bullet.center_y = enemy.center_y
            angle = math.atan2(enemy.center_y - self.objects[0].center_y, enemy.center_x - self.objects[0].center_x)
            bullet.angle = math.degrees(angle)
            bullet.change_x = - math.cos(angle) * BULLET_SPEED
            bullet.change_y = - math.sin(angle) * BULLET_SPEED
            if enemy.size == 0:
                enemy.recharge_time = 30
            elif enemy.size == 1:
                enemy.recharge_time = 60
            elif enemy.size == 2:
                enemy.recharge_time = 75
            self.enemy_bullet_list.append(bullet)
        else:
            enemy.recharge_time -= 1

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

    def default_tankette_spawn(self, frequency, size, recharge_time=0):
        """
        Creates a tankette
        :param frequency: frequency of spawn
        :param size: size using for creating bullets
        :param recharge_time: initial recharge time
        """
        if self.frame_count % (FPS * frequency) == 0:
            direct = random.choice([1, -1])
            file = "pictures/" + str(size) + "_tankette 0 .png"
            tankette = arcade.Sprite(file, flipped_horizontally=bool(abs(direct-1)/2))
            tankette.file = file
            tankette.size = size
            tankette.direct = direct
            tankette.time = 0  # initial existing time
            tankette.change_x = direct * TANKETTE_VELOCITIES[size]
            tankette.center_x = SCREEN_WIDTH/2 - direct * (SCREEN_WIDTH/2 + tankette.width)
            tankette.bottom = GROUND/2
            tankette.hp = TANKETTE_HPS[size]  # установление HP танкетки согласно ее размеру
            tankette.recharge_time = recharge_time
            self.ground_enemies.append(tankette)
            self.enemies.append(tankette)

    def default_drone_spawn(self, frequency):
        """
        Creates a drone
        :param frequency: frequency of spawn
        """
        if self.frame_count % (FPS * frequency) == 0:
            direct = random.choice([1, -1])
            drone = arcade.Sprite("pictures/drone.png")
            drone.type = "drone"
            drone.size = 0
            drone.center_x = SCREEN_WIDTH/2 - direct * (SCREEN_WIDTH/2 + drone.width)
            drone.top = random.randint(SCREEN_HEIGHT//2, SCREEN_HEIGHT)
            angle = math.atan2(drone.center_y - self.objects[0].center_y, drone.center_x - self.objects[0].center_x)
            drone.change_x = - DRONE_VELOCITY * math.cos(angle)
            drone.change_y = - DRONE_VELOCITY * math.sin(angle)
            drone.hp = 1

            # добавление дрона к соответствующим спискам врагов:
            self.enemy_kamikaze.append(drone)
            self.enemies.append(drone)

    def default_copter_spawn(self, frequency, size):
        """
        Creates a (heli)copter
        :param frequency: frequency of spawn
        :param size: size
        helicopter, helicopter
        """
        if self.frame_count % (FPS * frequency) == 0:
            direct = random.choice([1, -1])
            file = "pictures/" + str(size) + "_copter 0 .png"
            copter = arcade.Sprite(file)
            copter.type = "copter"
            copter.center_x = SCREEN_WIDTH/2 - direct * (SCREEN_WIDTH/2 + copter.width)
            copter.top = random.randint(SCREEN_HEIGHT//2, SCREEN_HEIGHT)
            copter.direct = direct
            copter.file = file
            copter.time = 0  # initial existing time

            angle = math.atan2(self.objects[0].center_y - copter.center_y, self.objects[0].center_x - copter.center_x)
            copter.change_x = COPTER_VELOCITY * math.cos(angle)
            copter.change_y = COPTER_VELOCITY * math.sin(angle)
            copter.hp = COPTER_HPS[size]
            copter.size = size

            copter.gun = arcade.Sprite("pictures/gun1.png")
            copter.gun.size = 0
            copter.gun.angle = math.degrees(angle) - 90
            copter.gun.center_x = copter.center_x
            copter.gun.top = copter.center_y
            copter.gun.recharge_time = 0

            self.air_enemies.append(copter)
            self.enemies.append(copter)
            self.guns.append(copter.gun)

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


def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
