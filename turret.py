import arcade
import random
import math
import os

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Sprites and Bullets Enemy Aims Example"
BULLET_SPEED = 64
mouse_x = 0
mouse_y = 0
GROUND = 60
TANK_VELOCITY = 1
FPS = 60


class MyGame(arcade.Window):
    """ Main application class """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color((255, 255, 255))

        self.frame_count = 0

        self.enemies = None
        self.bullet_list = None
        self.gun = None
        self.pillbox = None
        self.objects = None
        self.guns = None

    def setup(self):
        """ Set up the game and initialize the variables """

        self.enemies = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.objects = arcade.SpriteList()
        self.guns = arcade.SpriteList()

        pillbox = arcade.Sprite("pillbox.png", 1)
        pillbox.center_x = SCREEN_WIDTH/2
        pillbox.center_y = pillbox._height/2
        self.objects.append(pillbox)

        gun = arcade.Sprite("gun.png", 1)
        gun.center_x = SCREEN_WIDTH/2
        gun.center_y = pillbox._height + 4/9 * gun._width
        gun.angle = 180
        self.guns.append(gun)

    def on_draw(self):
        """Render the screen """

        arcade.start_render()
        arcade.draw_rectangle_filled(0, 0, SCREEN_WIDTH*2, GROUND, arcade.csscolor.GREEN)
        self.objects.draw()
        self.bullet_list.draw()
        self.guns.draw()
        self.enemies.draw()

    def on_update(self, delta_time):
        """The logic of game """

        self.frame_count += 1

        if self.frame_count % FPS*5 == 0:
            Rand = random.choice([0, SCREEN_WIDTH])
            if Rand == SCREEN_WIDTH:
                tankette = arcade.Sprite("tankette.png", flipped_horizontally=True)
                tankette.change_x = - TANK_VELOCITY
            else:
                tankette = arcade.Sprite("tankette.png")
                tankette.change_x = TANK_VELOCITY
            tankette.center_x = Rand
            tankette.top = GROUND + tankette._height/2
            self.enemies.append(tankette)

        for gun in self.guns:
            angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)
            gun.angle = math.degrees(angle) - 90

        for bullet in self.bullet_list:
            if bullet.top < 0 or bullet.top > SCREEN_HEIGHT or bullet.right < 0 or bullet.right > SCREEN_WIDTH:
                bullet.remove_from_sprite_lists()

        self.enemies.update()
        self.bullet_list.update()

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

            bullet.angle = math.degrees(angle)
            bullet.change_x = math.cos(angle) * BULLET_SPEED
            bullet.change_y = math.sin(angle) * BULLET_SPEED

            self.bullet_list.append(bullet)


def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()