import arcade.gui
import constants as const

enemies = {
    "tankette": {"sizes": [1, 2, 4], "frames": 2},
    "copter": {"sizes": [1], "frames": 6},
    "sparky": {"sizes": [20], "frames": 3}
}


def define_all(game):
    """
    Loads important elements of game
    """
    define_variables_and_spritelists(game)
    define_textures(game)
    define_sounds(game)


def define_variables_and_spritelists(game):
    """
    Loads some variables and initializes spritelists
    """
    game.frame_count = -1  # счётчик обновлений экрана
    game.score = 0  # счёт
    game.enemy_points = 0  # текущее значение очков врага
    game.spawn_timer = 0  # таймер, по которому рассчитывается спавн врагов
    game.cash = 0  # счётчик валюты
    game.text = "DEFEND THE COHORT OF LAST SURVIVORS!\n\nUSE MOUSE TO AIM AND FIRE\n\nSERVITUS IS CLOSING..."
    game.text_time = const.TEXT_TIME * 2  # таймер для корректного отображения текста
    game.health_hint_marker = False
    game.helicopter_helicopter_indicator = False
    game.enable_gun_switching = False
    game.airstrike_rockets = 0
    game.airmines = False
    game.airguns = False
    game.airmine_timer = 0
    game.coin_magnet = False
    game.lateral_weapons_damage_modifier = 1

    game.transparency = 0  # alpha of night desert and color filter
    game.cycle_number = 0  # number of cycle/2
    game.day_timer = 0  # нормированный на частоту смены дня и ночи счётчик времени
    game.airstrike_timer = -1

    game.clouds = arcade.SpriteList()
    game.icons = arcade.SpriteList()
    game.moneys = arcade.SpriteList()
    game.enemies = arcade.SpriteList()
    game.static_objects = arcade.SpriteList()
    game.ground_enemies = arcade.SpriteList()
    game.air_enemies = arcade.SpriteList()
    game.enemy_kamikaze = arcade.SpriteList()
    game.bullet_list = arcade.SpriteList()
    game.enemy_bullet_list = arcade.SpriteList()
    game.ground_lateral_weapons = arcade.SpriteList()
    game.objects = arcade.SpriteList()
    game.player_guns = arcade.SpriteList()
    game.player_autoguns = arcade.SpriteList()
    game.guns = arcade.SpriteList()
    game.booms = arcade.SpriteList()
    game.trash = arcade.SpriteList()
    game.lore = arcade.SpriteList()
    game.backgrounds = arcade.SpriteList()
    game.color_filters = arcade.SpriteList()
    game.sleeves = arcade.SpriteList()
    game.sparky_bullet_list = arcade.SpriteList()
    game.rocket_list = arcade.SpriteList()
    game.airmine_list = arcade.SpriteList()
    game.airgun_list = arcade.SpriteList()
    game.sparkle_list = arcade.SpriteList()


def define_textures(game):
    """
    Loads textures based on their filename
    """
    game.textures = {}
    for enemy in enemies.keys():
        for size in enemies[enemy]["sizes"]:
            for frame in range(enemies[enemy]["frames"]):
                file = "pictures/" + str(size) + "_" + enemy + " " + str(frame) + " .png"
                game.textures[file] = arcade.load_texture_pair(file)
                if enemy != "sparky":
                    file = "pictures/" + str(size) + "chromium" + "_" + enemy + " " + str(frame) + " .png"
                    game.textures[file] = arcade.load_texture_pair(file)

    for elem in ["airmine", "airgun"]:
        for frame in range(2):
            file = "pictures/" + elem + " " + str(frame) + " .png"
            game.textures[file] = arcade.load_texture_pair(file)


def define_sounds(game):
    """
    Loads sounds
    """
    game.main_sound = arcade.load_sound("sounds/ThomasBergersenImmortal.mp3", False)
    game.helicopter_crash = arcade.load_sound("sounds/helicopter_crash.mp3", False)
    game.end_of_game = arcade.load_sound("sounds/game_over.wav", False)
    game.laser_sound = arcade.load_sound("sounds/laser.mp3", False)
    game.minigun_sound = arcade.load_sound("sounds/minigun_fire.mp3", False)
    game.heal_sound = arcade.load_sound("sounds/heal.mp3", False)
    game.upgrade_sound = arcade.load_sound("sounds/upgrade.mp3", False)
    game.cannon_sound = arcade.load_sound("sounds/cannon_fire.mp3", False)
    game.coin_sound = arcade.load_sound("sounds/coin_pickup.wav", False)
    game.coin_score = arcade.load_sound("sounds/coin_score.wav", False)
    game.helicopter_helicopter = arcade.load_sound("sounds/helicopter, helicopter.mp3", False)
    game.sparky_spawn = arcade.load_sound("sounds/sparky_spawn.mp3", False)
    game.sparky_shot = arcade.load_sound("sounds/sparky_shot.mp3", False)
    game.sparky_hit = arcade.load_sound("sounds/sparky_hit.mp3", False)
    game.turret_switch = arcade.load_sound("sounds/technical_sound.mp3", False)
    game.thunder = arcade.load_sound("sounds/thunder.mp3", False)
    game.airstrike_calling = arcade.load_sound("sounds/airborne2.mp3", False)
    game.airstrike_inbound = arcade.load_sound("sounds/airstrike inbound.mp3", False)
    game.blast = arcade.load_sound("sounds/blast.mp3", False)
    game.radar = arcade.load_sound("sounds/radar.mp3", False)
    game.lore_sound = arcade.load_sound("sounds/Dark Tension Rising Music.mp3", False)
    game.ricochet = [0] * 2
    game.ricochet[0] = arcade.load_sound("sounds/ricochet1.mp3", False)
    game.ricochet[1] = arcade.load_sound("sounds/ricochet2.mp3", False)
