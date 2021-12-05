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
BULLET_SPEED = 64  # полная скорость пули
TANKETTE_VELOCITIES = [2, 1.5, 1]  # полные скорости танкеток (в соответствии с размером)
DRONE_VELOCITY = 3  # полная скорость дрона
BULLET_PENETRA = 2  # HP пули главной пушки

# время:
FPS = 60
FPB = 4  # frames per one texture image of explosion

# sounds:
main_sound = arcade.load_sound("sounds/background.m4a", False)
laser_sound = arcade.load_sound("sounds/laser.mp3", False)
helicopter_crash = arcade.load_sound("sounds/helicopter_crash.mp3", False)
end_of_game = arcade.load_sound("sounds/gameover.wav", False)


class MyGame(arcade.Window):
    """ Main application class """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.game_over = False
        arcade.set_background_color((255, 255, 255))

        self.frame_count = 0  # счётчик обновлений экрана

        self.ground_enemies = None  # наземные враги
        self.enemy_kamikaze = None  # враги-камикадзе: взрываются по достижении цели
        self.bullet_list = None  # список пуль
        self.enemy_bullet_list = None  # список вражеских снарядов
        self.objects = None  # объекты, представляющие стратегическую важность для игры
        self.guns = None  # пушки игрока
        self.booms = None  # список действующих анимаций взрывов

    def setup(self):
        """ Set up the game and initialize the variables """
        # sound:
        arcade.play_sound(main_sound, volume=0.2, looping=True)

        # инициализация различных списков:
        self.ground_enemies = arcade.SpriteList()
        self.enemy_kamikaze = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.objects = arcade.SpriteList()
        self.guns = arcade.SpriteList()
        self.booms = arcade.SpriteList()

        # инициализация главного холма (с записью его расположения на экране и помещением в список objects):
        pillbox = arcade.Sprite("pictures/pillbox.png", 1)
        pillbox.center_x = SCREEN_WIDTH/2
        pillbox.center_y = pillbox.height/2
        pillbox.hp = 40
        self.objects.append(pillbox)

        # инициализация главной пушки (с записью ее расположения на экране и помещением в список guns):
        gun = arcade.Sprite("pictures/gun.png", 1)
        gun.center_x = SCREEN_WIDTH/2
        gun.center_y = pillbox.height + 4/9 * gun.width
        self.guns.append(gun)

    def on_draw(self):
        """ Render the screen """

        arcade.start_render()

        # рисование земли:
        arcade.draw_rectangle_filled(0, 0, SCREEN_WIDTH*2, GROUND, arcade.color.EARTH_YELLOW)

        # рисование различных объектов:
        self.objects.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.guns.draw()
        self.ground_enemies.draw()
        self.enemy_kamikaze.draw()
        self.booms.draw()

        # рисование HP (health points) у наземных врагов и objects:
        for enemy in self.ground_enemies:
            arcade.draw_text(str(enemy.hp), enemy.center_x - enemy.width/2, enemy.top + 12,
                             arcade.color.FRENCH_WINE, 20, width=enemy.width, align="center")
        for object in self.objects:
            arcade.draw_text(str(object.hp), object.center_x - object.width/2, object.top + 80,
                             arcade.color.FRENCH_WINE, 25, width=object.width, align="center")

    def on_update(self, delta_time):
        """ Логика игры """
        if not self.game_over:

            # обновление счетчика кадров:
            self.frame_count += 1

            # регулярный спавн танкеток и дронов:
            self.default_tankette_spawn(frequency=3, size=0)
            self.default_tankette_spawn(frequency=6, size=1)
            self.default_tankette_spawn(frequency=11, size=2)
            self.default_drone_spawn(frequency=5)

            # обновление угла наклона главной пушки:
            for gun in self.guns:
                angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)
                gun.angle = math.degrees(angle) - 90

            for bullet in self.bullet_list:
                # проверка поражений целей игроком:
                hit_list = (arcade.check_for_collision_with_list(bullet, self.ground_enemies)
                            + arcade.check_for_collision_with_list(bullet, self.enemy_kamikaze))

                # обновление HP у врагов и пули; ее удаление в случае отсутствия HP:
                for enemy in hit_list:
                    if bullet.hp > 0:
                        enemy.hp -= 1
                        bullet.hp -= 1
                    else:
                        bullet.remove_from_sprite_lists()

                # удаление пули при ее покидании экрана и/или отсутствии HP:
                if (bullet.bottom < GROUND/2 or bullet.top > SCREEN_HEIGHT
                        or bullet.right < 0 or bullet.left > SCREEN_WIDTH
                        or bullet.hp <= 0):
                    bullet.remove_from_sprite_lists()

            for object in self.objects:
                # обновление HP игрока и замена текстуры холма при его занулении:
                if self.enemy_bullet_list is not None:
                    hit_list = arcade.check_for_collision_with_list(object, self.enemy_bullet_list)
                    for bullet in hit_list:
                        if bullet.size == 0:
                            object.hp -= 1
                        if bullet.size == 1:
                            object.hp -= 2
                        if bullet.size == 2:
                            object.hp -= 4

                        # зануление HP игрока при его возможном достижении отрицательного значения:
                        if object.hp < 0:
                            object.hp = 0

                        bullet.remove_from_sprite_lists()
                    # замена картинки холма при достижении нулевого HP игроком:
                    if object.hp == 0:
                        object.texture = arcade.load_texture("pictures/pillbox_destructed.png")
                        arcade.play_sound(end_of_game, volume=0.9)
                        self.game_over = True

            for enemy in self.ground_enemies:
                enemy.time += 1
                if enemy.hp <= 0:
                    # удаление танкетки при отсутствии у нее HP:
                    enemy.remove_from_sprite_lists()
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

            for enemy in self.enemy_kamikaze:
                if enemy.hp <= 0:
                    # удаление дрона с созданием на его месте взрыва:
                    self.create_boom(enemy.center_x, enemy.center_y, enemy.change_x, enemy.change_y)
                    enemy.remove_from_sprite_lists()

                    # включение звука взрыва:
                    arcade.play_sound(helicopter_crash, volume=0.8)
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
            self.ground_enemies.update()
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

        for gun in self.guns:

            # создание пули и помещении ее в список пуль игрока:
            bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
            bullet.center_x = gun.center_x
            bullet.center_y = gun.center_y
            angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)

            bullet.hp = BULLET_PENETRA
            bullet.angle = math.degrees(angle)
            bullet.change_x = math.cos(angle) * BULLET_SPEED
            bullet.change_y = math.sin(angle) * BULLET_SPEED

            arcade.play_sound(laser_sound, volume=0.7)

            self.bullet_list.append(bullet)

    def fire(self, enemy):
        """ Makes enemy firing: creates bullets if enemy is aimed and keep aiming if not """
        if enemy.recharge_time == 0:
            bullet = arcade.Sprite("pictures/" + str(enemy.size) + "_bullet.png", 1)
            bullet.size = enemy.size
            bullet.center_x = enemy.center_x
            bullet.center_y = enemy.center_y
            bullet.change_x = BULLET_SPEED * enemy.direct

            # обновление времени перезарядки для танкетки:
            if enemy.size == 0:
                enemy.recharge_time = 30
            elif enemy.size == 1:
                enemy.recharge_time = 60
            elif enemy.size == 2:
                enemy.recharge_time = 75
            self.enemy_bullet_list.append(bullet)
        else:
            # ход времени счетчика перезарядки:
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
        boom.change_x = Vx/3  # keeps moving
        boom.change_y = Vy/3 - 1  # and slowly falls down
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
            tankette.bottom = GROUND/2 - 4

            # установление HP танкетки согласно ее размеру:
            if size == 0:
                tankette.hp = 3
            elif size == 1:
                tankette.hp = 6
            elif size == 2:
                tankette.hp = 10

            tankette.recharge_time = recharge_time

            # добавление танкетки к соответствующему списку врагов:
            self.ground_enemies.append(tankette)

    def default_drone_spawn(self, frequency):
        """
        Creates a drone
        :param frequency: frequency of spawn
        """
        if self.frame_count % (FPS * frequency) == 0:
            direct = random.choice([1, -1])
            drone = arcade.Sprite("pictures/drone.png")
            drone.center_x = SCREEN_WIDTH / 2 - direct * (SCREEN_WIDTH / 2 + drone.width)
            drone.top = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT)
            angle = math.atan2(drone.center_y - self.objects[0].center_y, drone.center_x - self.objects[0].center_x)
            drone.change_x = - DRONE_VELOCITY * math.cos(angle)
            drone.change_y = - DRONE_VELOCITY * math.sin(angle)
            drone.hp = 1

            # добавление дрона к соответствующему списку врагов:
            self.enemy_kamikaze.append(drone)

    def next_frame(self, object, frames=2):
        """
        Анимирует объект путем регулярной замены его текстуры.
        Takes info about current frame from filename.
        Changes texture by changing number of frame in filename.
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
