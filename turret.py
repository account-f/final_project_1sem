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
TANK_VELOCITY = 1
FPS = 60
BULLET_PENETRA = 2  # armor penetration


class MyGame(arcade.Window):
    """ Main application class """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.game_over = False
        arcade.set_background_color((255, 255, 255))

        self.frame_count = 0

        self.enemies = None
        self.bullet_list = None
        self.enemy_bullet_list = None
        self.pillbox = None
        self.objects = None
        self.guns = None

    def setup(self):
        """ Set up the game and initialize the variables """

        self.enemies = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.objects = arcade.SpriteList()
        self.guns = arcade.SpriteList()

        pillbox = arcade.Sprite("pillbox.png", 1)
        pillbox.center_x = SCREEN_WIDTH/2
        pillbox.center_y = pillbox.height/2
        pillbox.hp = 40
        self.objects.append(pillbox)

        gun = arcade.Sprite("gun.png", 1)
        gun.center_x = SCREEN_WIDTH/2
        gun.center_y = pillbox.height + 4/9 * gun.width
        self.guns.append(gun)

    def on_draw(self):
        """Render the screen """

        arcade.start_render()
        arcade.draw_rectangle_filled(0, 0, SCREEN_WIDTH*2, GROUND, arcade.color.EARTH_YELLOW)
        self.objects.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.guns.draw()
        self.enemies.draw()
        for enemy in self.enemies:
            arcade.draw_text(str(enemy.hp), enemy.center_x - enemy.width/2, enemy.top + 12,
                             arcade.color.FRENCH_WINE, 20, width=enemy.width, align="center")
        for object in self.objects:
            arcade.draw_text(str(object.hp), object.center_x - object.width/2, object.top + 80,
                             arcade.color.FRENCH_WINE, 25, width=object.width, align="center")

    def on_update(self, delta_time):
        """The logic of game """

        if not self.game_over:
            self.frame_count += 1

            if self.frame_count % (FPS * 2) == 0:
                direct = random.choice([1, -1])
                if direct == -1:
                    tankette = arcade.Sprite("tankette.png", flipped_horizontally=True)
                else:
                    tankette = arcade.Sprite("tankette.png")
                tankette.direct = direct
                tankette.change_x = direct * TANK_VELOCITY
                tankette.center_x = SCREEN_WIDTH/2 - direct * (SCREEN_WIDTH/2 + tankette.width)
                tankette.top = GROUND + tankette.height/2
                tankette.hp = 5
                tankette.recharge_time = 0
                self.enemies.append(tankette)

            for gun in self.guns:
                angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)
                gun.angle = math.degrees(angle) - 90

            for bullet in self.bullet_list:
                hit_list = arcade.check_for_collision_with_list(bullet, self.enemies)
                for enemy in hit_list:
                    if bullet.hp > 0:
                        enemy.hp -= 1
                        bullet.hp -= 1
                    else:
                        bullet.remove_from_sprite_lists()

                if (bullet.top < 0 or bullet.bottom > SCREEN_HEIGHT
                        or bullet.right < 0 or bullet.left > SCREEN_WIDTH):
                    bullet.remove_from_sprite_lists()

            for object in self.objects:
                if self.enemy_bullet_list is not None:
                    hit_list = arcade.check_for_collision_with_list(object, self.enemy_bullet_list)
                    for bullet in hit_list:
                        object.hp -= 2
                        bullet.remove_from_sprite_lists()
                    if object.hp <= 0:
                        object.texture = arcade.load_texture("pillbox_destructed.png")
                        self.game_over = True

            for enemy in self.enemies:
                if enemy.hp <= 0:
                    enemy.remove_from_sprite_lists()
                elif abs(enemy.center_x - SCREEN_WIDTH/2) < SCREEN_WIDTH/6:
                    self.fire(enemy)
                    enemy.change_x = 0

            self.enemies.update()
            self.bullet_list.update()
            self.enemy_bullet_list.update()

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """ Called whenever the mouse moves """
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked """

        for gun in self.guns:
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
        if enemy.recharge_time == 0:
            bullet = arcade.Sprite("bullet.png", 1)
            bullet.center_x = enemy.center_x
            bullet.center_y = enemy.center_y
            bullet.change_x = BULLET_SPEED * enemy.direct
            enemy.recharge_time = 75
            self.enemy_bullet_list.append(bullet)
        else:
            enemy.recharge_time -= 1


def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
