import arcade
import arcade.gui
import random
import math
import constants as const


def drone(game, size):
    """
    Создаёт дрон-камикадзе
    :param game: игра, в которой происходит изменение
    :param size: размер
    """
    direct = random.choice([1, -1])
    drone = arcade.Sprite("pictures/drone.png")
    drone.size = size
    drone.center_x = const.SCREEN_WIDTH/2 - direct * (const.SCREEN_WIDTH/2 + drone.width)
    drone.top = random.randint(const.SCREEN_HEIGHT//2, const.SCREEN_HEIGHT)
    angle = math.atan2(drone.center_y - game.objects[0].center_y, drone.center_x - game.objects[0].center_x)
    drone.change_x = - const.DRONE_VELOCITY * math.cos(angle)
    drone.change_y = - const.DRONE_VELOCITY * math.sin(angle)
    drone.hp = 1

    # добавление дрона к соответствующим спискам врагов:
    game.enemy_kamikaze.append(drone)
    game.enemies.append(drone)


class Enemy(arcade.Sprite):
    def __init__(self, filename):
        super().__init__(filename)
        self.filename = filename
        self.hp = 1
        self.size = 1


class AirEnemy(Enemy):
    def __init__(self, filename, game):
        Enemy.__init__(self, filename)
        direct = random.choice([1, -1])
        self.center_x = const.SCREEN_WIDTH / 2 - direct * (const.SCREEN_WIDTH / 2 + self.width)
        self.top = random.randint(const.SCREEN_HEIGHT // 2, const.SCREEN_HEIGHT)
        angle = math.atan2(self.center_y - game.objects[0].center_y, self.center_x - game.objects[0].center_x)
        self.change_x = - const.DRONE_VELOCITY * math.cos(angle)
        self.change_y = - const.DRONE_VELOCITY * math.sin(angle)


class Drone(AirEnemy):
    def __init__(self, filename, game):
        AirEnemy.__init__(self, filename, game)
        self.filename = "pictures/drone.png"
        game.enemy_kamikaze.append(self)
        game.enemies.append(self)

