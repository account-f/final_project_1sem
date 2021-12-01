import arcade
import random
import math
import os

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Turret"
BULLET_SPEED = 64
mouse_x = 0
mouse_y = 0
GROUND = 60
TANKETTE_VELOCITIES = [2, 1.5, 1]
DRONE_VELOCITY = 3
FPS = 60
BULLET_PENETRA = 2  # armor penetration
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

        self.ground_enemies = None  # наземные враги
        self.enemy_kamikaze = None  # враги-камикадзе: взрываются по достижении цели
        self.bullet_list = None  # список пуль
        self.enemy_bullet_list = None  # список вражеских снарядов
        self.objects = None  # объекты, представляющие стратегическую важность для игры
        self.guns = None  # пушки игрока
        self.booms = None  # список действующих анимаций взрывов

    def setup(self):
        """ Set up the game and initialize the variables """

        self.ground_enemies = arcade.SpriteList()
        self.enemy_kamikaze = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.objects = arcade.SpriteList()
        self.guns = arcade.SpriteList()
        self.booms = arcade.SpriteList()

        pillbox = arcade.Sprite("pictures/pillbox.png", 1)
        pillbox.center_x = SCREEN_WIDTH/2
        pillbox.center_y = pillbox.height/2
        pillbox.hp = 40
        self.objects.append(pillbox)

        gun = arcade.Sprite("pictures/gun.png", 1)
        gun.center_x = SCREEN_WIDTH/2
        gun.center_y = pillbox.height + 4/9 * gun.width
        self.guns.append(gun)

    def on_draw(self):
        """ Render the screen """

        arcade.start_render()
        arcade.draw_rectangle_filled(0, 0, SCREEN_WIDTH*2, GROUND, arcade.color.EARTH_YELLOW)
        self.objects.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.guns.draw()
        self.ground_enemies.draw()
        self.enemy_kamikaze.draw()
        self.booms.draw()
        for enemy in self.ground_enemies:
            # рисование хп у наземных врагов
            arcade.draw_text(str(enemy.hp), enemy.center_x - enemy.width/2, enemy.top + 12,
                             arcade.color.FRENCH_WINE, 20, width=enemy.width, align="center")
        for object in self.objects:
            arcade.draw_text(str(object.hp), object.center_x - object.width/2, object.top + 80,
                             arcade.color.FRENCH_WINE, 25, width=object.width, align="center")

    def on_update(self, delta_time):
        """The logic of game """

        if not self.game_over:
            self.frame_count += 1

            self.default_tankette_spawn(frequency=3, size=0)
            self.default_tankette_spawn(frequency=6, size=1)
            self.default_tankette_spawn(frequency=11, size=2)
            self.default_drone_spawn(frequency=5)

            for gun in self.guns:
                angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)
                gun.angle = math.degrees(angle) - 90

            for bullet in self.bullet_list:
                # поражение целей игроком
                hit_list = (arcade.check_for_collision_with_list(bullet, self.ground_enemies)
                            + arcade.check_for_collision_with_list(bullet, self.enemy_kamikaze))
                for enemy in hit_list:
                    if bullet.hp > 0:
                        enemy.hp -= 1
                        bullet.hp -= 1
                    else:
                        bullet.remove_from_sprite_lists()

                if (bullet.top < 0 or bullet.bottom > SCREEN_HEIGHT
                        or bullet.right < 0 or bullet.left > SCREEN_WIDTH
                        or bullet.hp <= 0):
                    # вылет пули за пределы экрана
                    bullet.remove_from_sprite_lists()

            for object in self.objects:
                # изменение текстуры дота по истечении хп
                if self.enemy_bullet_list is not None:
                    hit_list = arcade.check_for_collision_with_list(object, self.enemy_bullet_list)
                    for bullet in hit_list:
                        if bullet.size == 0:
                            object.hp -= 1
                        if bullet.size == 1:
                            object.hp -= 2
                        if bullet.size == 2:
                            object.hp -= 4
                        bullet.remove_from_sprite_lists()
                    if object.hp <= 0:
                        object.texture = arcade.load_texture("pictures/pillbox_destructed.png")
                        self.game_over = True

            for enemy in self.ground_enemies:
                if enemy.hp <= 0:
                    enemy.remove_from_sprite_lists()
                else:
                    distance = abs(enemy.center_x - SCREEN_WIDTH / 2)
                    if enemy.size == 0 and distance < SCREEN_WIDTH/6:
                        self.fire(enemy)
                        enemy.change_x = 0
                    if enemy.size == 1 and distance < SCREEN_WIDTH/5:
                        self.fire(enemy)
                        enemy.change_x = 0
                    if enemy.size == 2 and distance < SCREEN_WIDTH/4:
                        self.fire(enemy)
                        enemy.change_x = 0

            for enemy in self.enemy_kamikaze:
                if enemy.hp <= 0:
                    self.create_boom(enemy.center_x, enemy.center_y, enemy.change_x, enemy.change_y)
                    enemy.remove_from_sprite_lists()
                else:
                    hit_list = arcade.check_for_collision_with_list(enemy, self.objects)
                    for object in hit_list:
                        object.hp -= 10
                        enemy.hp = 0

            for boom in self.booms:
                boom.count += 1
                if boom.count % FPB == 0:
                    # updates every FPB frames
                    file = "pictures/boom" + str(boom.count // FPB) + ".png"
                    if os.path.exists(file):
                        # file named as boom1, boom2 etc; this checks existing in agreement with boom.count
                        boom.texture = arcade.load_texture(file)
                    else:
                        boom.remove_from_sprite_lists()

            self.ground_enemies.update()
            self.bullet_list.update()
            self.enemy_bullet_list.update()
            self.enemy_kamikaze.update()
            self.booms.update()

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """ Called whenever the mouse moves """
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked """

        for gun in self.guns:
            # creates bullet
            bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
            bullet.center_x = gun.center_x
            bullet.center_y = gun.center_y
            angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)

            bullet.hp = BULLET_PENETRA
            bullet.angle = math.degrees(angle)
            bullet.change_x = math.cos(angle) * BULLET_SPEED
            bullet.change_y = math.sin(angle) * BULLET_SPEED

            self.bullet_list.append(bullet)

    def fire(self, enemy):
        """ Makes enemy firing: creates bullets if enemy is aimed and keep aiming if not """
        if enemy.recharge_time == 0:
            bullet = arcade.Sprite("pictures/" + str(enemy.size) + "_bullet.png", 1)
            bullet.size = enemy.size
            bullet.center_x = enemy.center_x
            bullet.center_y = enemy.center_y
            bullet.change_x = BULLET_SPEED * enemy.direct
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
            if direct == -1:
                tankette = arcade.Sprite("pictures/" + str(size) + "_tankette.png", flipped_horizontally=True)
            else:
                tankette = arcade.Sprite("pictures/" + str(size) + "_tankette.png")
            tankette.size = size
            tankette.direct = direct
            tankette.change_x = direct * TANKETTE_VELOCITIES[size]
            tankette.center_x = SCREEN_WIDTH/2 - direct * (SCREEN_WIDTH/2 + tankette.width)
            tankette.bottom = GROUND/2 - 4
            if size == 0:
                tankette.hp = 3
            elif size == 1:
                tankette.hp = 6
            elif size == 2:
                tankette.hp = 10
            tankette.recharge_time = recharge_time
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
            self.enemy_kamikaze.append(drone)


def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
