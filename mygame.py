import math
import os
import random

import arcade
import arcade.gui
import numpy

import constants as const
import enemies
import resources


class QuitButton(arcade.gui.UIFlatButton):
    """ Класс описывает поведение кнопки выхода в меню """
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        """
        Вызывается при нажатии
        :param event: событие, при котором функция вызывается
        """
        arcade.exit()


class StartButton(arcade.gui.UIFlatButton):
    """ Класс описывает поведение кнопки старта в меню """
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        """
        Вызывается при нажатии
        :param event: событие, при котором функция вызывается
        """
        global gamemode
        gamemode = "lore"


class MyGame(arcade.Window):
    """ Основной класс программы """

    def __init__(self, width, height, title):
        """
        Конструктор класса MyGame: создаёт окно с игрой
        :param width: ширина окна
        :param height: высота окна
        :param title: надпись на окне - название игры
        """
        super().__init__(width, height, title)
        global gamemode

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.game_over = False
        arcade.set_background_color(arcade.color.ARSENIC)

        self.current_player = None

        resources.define_all(self)

        # инициализация фона и установка его координат:
        self.background = arcade.Sprite("pictures/desert.png")  # фоновый рисунок
        self.background.center_x = const.SCREEN_WIDTH/2
        self.background.center_y = const.SCREEN_HEIGHT/2

        self.max_enemy_points = 3  # initial number of enemy points, using to spawn
        self.mouse_pressed_test = False  # variable checks if key button IS pressed

        # настройка предыгрового меню:
        gamemode = "menu"
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout()

        # добавление кнопки старта:
        start_button = StartButton(text='Start', width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        # кнопки выхода:
        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)

        # pause mode:
        self.pause = False

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def setup(self):
        """ Настройка игры и инициализация переменных """
        # фоновая музыка:
#        arcade.play_sound(self.main_sound, volume=0.5, looping=True)

        # инициализация главного холма (с записью его расположения на экране и помещением в список objects):
        pillbox = arcade.Sprite("pictures/pillbox.png")
        pillbox.center_x = const.SCREEN_WIDTH/2
        pillbox.center_y = pillbox.height/2
        pillbox.max_hp = 50
        pillbox.hp = pillbox.max_hp
        self.objects.append(pillbox)

        # инициализация главной пушки (с записью ее расположения на экране и помещением в список player_guns):
        initial_gun = arcade.Sprite("pictures/initial_gun.png")
        initial_gun.center_x = const.SCREEN_WIDTH/2
        initial_gun.center_y = pillbox.height + 4/9 * initial_gun.width
        initial_gun.damage = 1
        initial_gun.penetra = 1
        initial_gun.fire_type = "ball"
        initial_gun.autofire = False
        initial_gun.rate = 2/const.FPS  # скорострельность: создаёт 2 пули за характерное время FPS
        initial_gun.recharge_time = 0
        self.player_guns.append(initial_gun)

        # инициализация иконки деталей:
        cash_icon = arcade.Sprite("pictures/money_icon.png")
        cash_icon.center_x = const.SCREEN_WIDTH/2 - 100 - cash_icon.width
        cash_icon.center_y = const.SCREEN_HEIGHT - 40 + cash_icon.height/2
        self.icons.append(cash_icon)

        # инициализация текста сюжета:
        self.create_lore()

        # добавление второго слоя фона:
        background = arcade.Sprite("pictures/desert_night.png")
        background.center_x = const.SCREEN_WIDTH/2
        background.center_y = const.SCREEN_HEIGHT/2
        background.alpha = 0
        self.backgrounds.append(background)

        # color filter, day-night cycle:
        filter = arcade.Sprite("pictures/filter_night.png")
        filter.center_x = const.SCREEN_WIDTH/2
        filter.center_y = const.SCREEN_HEIGHT/2
        filter.alpha = 0
        self.color_filters.append(filter)

    def on_draw(self):
        """ Отрисовывание экрана """

        if gamemode == "menu":
            arcade.start_render()
            self.manager.draw()
            return None

        elif gamemode == "lore":
            self.manager.disable()
            arcade.start_render()

            # рисование фона
            self.background.draw()

            arcade.draw_text("Press SPACE to skip", const.SCREEN_WIDTH/3, const.SCREEN_WIDTH/20,
                             arcade.color.WHITE, 16, width=const.SCREEN_WIDTH, align="center",
                             font_name="Kenney Future")

            # рисование текста сюжета до начала игры:
            for lore in self.lore:
                arcade.draw_text(const.lore_text, lore.center_x, lore.center_y,
                                 arcade.color.BLACK, 40, width=2 * const.SCREEN_WIDTH/3, align="center",
                                 font_name="Kenney Pixel")

        elif gamemode == "started":
            self.manager.disable()
            arcade.start_render()

            # рисование фона и земли:
            self.background.draw()
            self.backgrounds.draw()
            arcade.draw_rectangle_filled(const.SCREEN_WIDTH/2, const.GROUND/2, const.SCREEN_WIDTH, 8, (163, 109, 97))
            arcade.draw_rectangle_filled(const.SCREEN_WIDTH/2, const.GROUND/4, const.SCREEN_WIDTH, const.GROUND/2, (226, 198, 131))

            # рисование различных объектов:
            self.clouds.draw()
            self.icons.draw()
            self.moneys.draw()
            self.ground_lateral_weapons.draw()
            self.airmine_list.draw()
            self.airgun_list.draw()
            self.objects.draw()
            self.bullet_list.draw()
            self.static_objects.draw()
            self.enemy_bullet_list.draw()
            self.sleeves.draw()
            self.player_guns.draw()
            self.player_autoguns.draw()
            self.enemies.draw()
            self.guns.draw()
            self.rocket_list.draw()
            self.sparky_bullet_list.draw()
            self.booms.draw()
            self.sparkle_list.draw()
            self.color_filters.draw()

            # рисование HP (health points) у наземных врагов и objects:
            for enemy in self.enemies:
                if enemy.hp > 0:
                    arcade.draw_text(str(enemy.hp), enemy.center_x - enemy.width/2, enemy.top + 6,
                                     arcade.color.LAVA, 16, width=int(enemy.width), align="center",
                                     font_name="Kenney Future")

            for object in self.objects:
                arcade.draw_text(str(object.hp), object.center_x - object.width/2, object.top + 80,
                                 arcade.color.MEDIUM_PERSIAN_BLUE, 25, width=int(object.width), align="center",
                                 font_name="Kenney Future")

            # рисование текста со счётом и монетами:
            arcade.draw_text("SCORE: " + str(self.score), const.SCREEN_WIDTH/2 + 100, const.SCREEN_HEIGHT - 40,
                             arcade.color.MEDIUM_PERSIAN_BLUE, 25, font_name="Kenney Future")

            if self.cash >= 10 and self.objects[0].max_hp - self.objects[0].hp >= 10:
                arcade.draw_text(str(self.cash), const.SCREEN_WIDTH/2 - 100, const.SCREEN_HEIGHT - 40,
                                 arcade.color.DARK_PASTEL_GREEN, 25, font_name="Kenney Future")
            else:
                arcade.draw_text(str(self.cash), const.SCREEN_WIDTH/2 - 100, const.SCREEN_HEIGHT - 40,
                                 arcade.color.MEDIUM_PERSIAN_BLUE, 25, font_name="Kenney Future")

            if self.text_time >= 0:
                arcade.draw_text(self.text, 0, 3 * const.SCREEN_HEIGHT / 4,
                                 arcade.color.WHITE, 25, font_name="Kenney Future",
                                 width=const.SCREEN_WIDTH, align="center")

            if self.pause:
                arcade.draw_text("PRESS SPACE TO CONTINUE", 0, const.SCREEN_HEIGHT/8,
                                 arcade.color.WHITE, 18, font_name="Kenney Future",
                                 width=const.SCREEN_WIDTH, align="center")

    def on_update(self, delta_time):
        """ Вся логика игры здесь """
        global gamemode
        if gamemode == "lore":
            self.lore.update()
            for lore in self.lore:
                if lore.time == 1:
                    arcade.play_sound(self.thunder)
                    self.current_player = self.lore_sound.play(speed=0.8)
                elif lore.time == const.lore_time:
                    gamemode = "started"
                    self.trash.append(lore)
                    arcade.stop_sound(self.current_player)
                    self.current_player = self.main_sound.play(volume=0.5, loop=True)

                lore.time += 1

        elif not self.game_over and gamemode == "started" and not self.pause:

            # обновление счетчика кадров и таймера для текста:
            self.frame_count += 1
            self.text_time -= 1
            if self.airstrike_timer > 0:
                self.airstrike_timer -= 1
            elif self.airstrike_timer == 0 and self.airstrike_rockets > 0:
                self.screen_text("AIRSTRIKE IS READY!")

            self.spawn()
            self.clouds_spawn()

            for gun in self.player_autoguns:
                self.autoguns_fire(gun)

            if self.airmines:
                self.airmines_spawn()

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
                    reflect = False
                    if bullet.fire_type in ["ball", "ball2", "high_velocity_bullet"] and const.chromium_upgrade == 1:
                        reflect = numpy.random.choice([True, False], p=[0.05, 0.95])
                    # обновление HP у врагов и пули; ее удаление в случае отсутствия HP:
                    if bullet.hp > 0:
                        if reflect:
                            direct_change = random.choice([-1, 1])
                            bullet.change_x = direct_change * bullet.change_x
                            bullet.change_y = - direct_change * bullet.change_y
                            bullet.angle = math.degrees(math.atan2(bullet.change_y, bullet.change_x))

                            for i in range(random.randint(2, 6)):
                                sparkle = arcade.Sprite("pictures/" + str(random.choice(["small_", ""])) + "sparkle" + str(random.randint(1, 2)) + ".png")
                                sparkle.center_x = enemy.center_x
                                sparkle.center_y = enemy.center_y

                                angle = math.atan2(bullet.change_y, bullet.change_x)
                                delta_angle = random.randint(-10, 10)  # разброс
                                angle += delta_angle * math.pi / 180
                                velocity = math.sqrt(bullet.change_x**2 + bullet.change_y**2) / 10

                                sparkle.change_x = velocity * math.sin(angle)
                                sparkle.change_y = velocity * math.cos(angle)
                                sparkle.angle = math.degrees(angle)
                                sparkle.time = 0

                                self.sparkle_list.append(sparkle)

                            arcade.play_sound(self.ricochet[random.choice([0, 1])], volume=0.6)
                        else:
                            enemy.hp -= bullet.damage
                            bullet.hp -= 1
                    else:
                        bullet.remove_from_sprite_lists()
                        self.trash.append(bullet)
                if ((bullet.center_x - self.objects[0].center_x) ** 2 + (bullet.center_y - self.objects[0].center_y) ** 2 >= 2000 ** 2
                        or bullet.hp <= 0):
                    # удаление пули при ее покидании экрана и/или отсутствии HP:
                    bullet.remove_from_sprite_lists()
                    self.trash.append(bullet)
                bullet.change_y -= const.G_for_bullets

            for airmine in self.airmine_list:
                airmine.time += 1
                if airmine.time % const.FPB == 0:
                    self.next_frame(airmine, frames=2)

                hit_list = (arcade.check_for_collision_with_list(airmine, self.enemies))
                for enemy in hit_list:
                    enemy.hp -= airmine.damage
                    self.create_boom(airmine.center_x, airmine.center_y, 0, 0, 3)
                    circle = arcade.SpriteCircle(const.AIRSTRIKE_ROCKET_BLAST_RADIUS, arcade.color.WHITE)
                    circle.center_x = airmine.center_x
                    circle.center_y = airmine.center_y
                    hit_list2 = (arcade.check_for_collision_with_list(circle, self.enemies))
                    for elem in hit_list2:
                        elem.hp -= airmine.damage
                    arcade.play_sound(self.blast)
                    airmine.remove_from_sprite_lists()
                    self.trash.append(airmine)
                    self.trash.append(circle)
                if (airmine.center_x - airmine.x)**2 + (airmine.center_y - airmine.y)**2 <= (airmine.width + airmine.height)**2:
                    airmine.change_y = 0
                    airmine.change_x = 0

            for airgun in self.airgun_list:
                airgun.time += 1
                if airgun.time % const.FPB == 0:
                    self.next_frame(airgun, frames=2)

            for enemy in self.ground_enemies:
                enemy.time += 1
                if enemy.hp <= 0:
                    self.generate_money(enemy)
                    if len(self.moneys) >= 10 and self.frame_count <= const.FPS * 90:
                        self.screen_text("DON'T FORGET COLLECT DETAILS!")
                    # удаление врага при отсутствии HP:
                    enemy.remove_from_sprite_lists()
                    self.trash.append(enemy)
                    self.score += enemy.size  # начисление очков в зависимости от размера врага
                else:
                    distance = abs(enemy.center_x - const.SCREEN_WIDTH / 2)

                    # остановка на определенном расстоянии от холма (в зависимости от размера):
                    if ((enemy.size == 1 and distance < const.SCREEN_WIDTH/6) or
                            (enemy.size == 2 and distance < const.SCREEN_WIDTH/5) or
                            (enemy.size == 4 and distance < const.SCREEN_WIDTH/4) or
                            (enemy.size == 20 and distance < const.SCREEN_WIDTH/4 and enemy.recharge_time >= 0)):
                        enemy.change_x = 0
                        self.fire(enemy)

                    if enemy.sort == "sparky":
                        if enemy.time % int(const.FPB*1.5) == 0 and enemy.recharge_time >= 0:
                            self.next_frame(enemy, frames=3)
                        if abs(enemy.change_x) > 0 > enemy.recharge_time:
                            # friction to sparky after shot
                            enemy.change_x += enemy.direct/2
                    elif enemy.sort == "tankette":
                        if enemy.time % (const.FPB*2) == 0 and enemy.change_x != 0:
                            self.next_frame(enemy, frames=2)

            for enemy in self.air_enemies:
                enemy.gun.angle = math.degrees(math.atan2(enemy.center_y - self.objects[0].center_y,
                                                          enemy.center_x - self.objects[0].center_x)) + 90
                enemy.time += 1
                if enemy.hp <= 0:
                    self.generate_money(enemy)
                    enemy.remove_from_sprite_lists()
                    enemy.gun.remove_from_sprite_lists()
                    self.trash.append(enemy)
                    self.trash.append(enemy.gun)
                    self.score += enemy.size  # начисление очков в зависимости от размера врага
                else:
                    if enemy.time % (const.FPB/2) == 0:
                        self.next_frame(enemy, frames=6)
                    if enemy.type == 2 and enemy.time >= const.FPS:
                        self.fire(enemy.gun)
                    if ((enemy.center_x - self.objects[0].center_x) ** 2 +
                            (enemy.center_y - self.objects[0].center_y) ** 2
                            <= (const.SCREEN_HEIGHT / 3) ** 2):
                        enemy.change_x = 0
                        enemy.change_y = 0
                        enemy.gun.change_x = 0
                        enemy.gun.change_y = 0
                        self.fire(enemy.gun)

                if (enemy.center_x < 0 or enemy.center_x > const.SCREEN_WIDTH or
                        enemy.center_y < 0 or enemy.center_y > const.SCREEN_HEIGHT):
                    enemy.recharge_time = 10  # enemy.recharge_time не достигнет 0, если enemy не на экране
                if (enemy.center_x < - const.TOLERANCE or enemy.center_x > const.SCREEN_WIDTH + const.TOLERANCE or
                        enemy.center_y < - const.TOLERANCE or enemy.center_y > const.SCREEN_HEIGHT + const.TOLERANCE):
                    enemy.remove_from_sprite_lists()
                    self.trash.append(enemy)
                    if hasattr("enemy", "gun") is True:
                        enemy.gun.remove_from_sprite_lists()
                        self.trash.append(enemy.gun)

            for enemy in self.enemy_kamikaze:
                if enemy.hp <= 0:
                    # удаление дрона с созданием на его месте взрыва:
                    self.create_boom(enemy.center_x, enemy.center_y, enemy.change_x, enemy.change_y, 1)
                    enemy.remove_from_sprite_lists()
                    self.trash.append(enemy)
                    self.score += enemy.size  # начисление очков в зависимости от размера врага

                    # включение звука взрыва:
                    arcade.play_sound(self.helicopter_crash, volume=0.2)
                else:
                    # проверка удара дроном по игроку с изменением HP игрока и занулением HP дрона:
                    hit_list = arcade.check_for_collision_with_list(enemy, self.objects)
                    for object in hit_list:
                        object.hp -= 10

                        self.create_boom(enemy.center_x, enemy.center_y, enemy.change_x, enemy.change_y, 1)
                        enemy.remove_from_sprite_lists()
                        self.trash.append(enemy)
                        arcade.play_sound(self.helicopter_crash, volume=0.2)

            for boom in self.booms:
                # анимация взрыва:
                boom.count += 1
                if boom.count % const.FPB == 0:
                    # обновляется каждые FPB кадров
                    file = "pictures/boom" + str(boom.type) + "_" + str(boom.count // const.FPB) + ".png"
                    if os.path.exists(file):
                        # файлы наз. boom1, boom2 итд; условие проверяет существование файла и изменяет текстуру
                        boom.texture = arcade.load_texture(file)
                    else:
                        boom.remove_from_sprite_lists()
                        self.trash.append(boom)

            for sparkle in self.sparkle_list:
                if sparkle.time >= const.FPS/4:
                    sparkle.remove_from_sprite_lists()
                    self.trash.append(sparkle)
                else:
                    sparkle.time += 1

            for object in self.objects:
                # обновление HP игрока и замена текстуры холма при его занулении:
                hit_list = arcade.check_for_collision_with_list(object, self.enemy_bullet_list)
                for bullet in hit_list:
                    object.hp -= bullet.size

                    bullet.remove_from_sprite_lists()
                    self.trash.append(bullet)

                hit_list = arcade.check_for_collision_with_list(object, self.sparky_bullet_list)
                for bullet in hit_list:
                    if not bullet.collision:
                        # HP removes in another part. Here comes the boom
                        self.create_boom(object.center_x, object.center_y, bullet.change_x/4, 0, 2)
                        bullet.collision = True
                        arcade.play_sound(self.sparky_hit, volume=0.5)

                if object.hp <= 0:
                    # замена картинки холма при достижении нулевого HP игроком:
                    object.texture = arcade.load_texture("pictures/pillbox_destructed.png")
                    object.hp = 0
                    arcade.play_sound(self.thunder)
                    self.screen_text("HUMANITY WAS EXCLUDED FROM EXISTENCE." \
                                     "\n\nSERVITUS HAS BECOME\nTHE ONLY FORM OF LIFE ON THE EARTH.")
                    self.game_over = True
                    print("Your score: ", self.score)
                    print("You have my respect, Player.")

            # поведение и система начисление деталей:
            for money in self.moneys:
                if money.caught_up is False:
                    money.change_y -= const.G_for_money
                if money.bottom <= const.GROUND/2 + 4 and money.caught_up is False:
                    money.change_y = 0
                    if not self.coin_magnet:
                        money.change_x = 0
                    else:
                        money.change_x = (self.objects[0].center_x - money.center_x)/abs(self.objects[0].center_x - money.center_x)

                if ((math.dist([mouse_x, mouse_y], [money.center_x, money.center_y]) <= 20 or
                        arcade.check_for_collision(self.objects[0], money)) and money.caught_up == False):
                    # собирание монет мышкой или падение монет прямо к доту:
                    arcade.play_sound(self.coin_sound, volume=0.3)
                    angle = math.atan2(self.icons[0].center_y - money.center_y, self.icons[0].center_x - money.center_x)
                    money.change_x = math.cos(angle) * 32
                    money.change_y = math.sin(angle) * 32
                    money.caught_up = True
                if math.dist([self.icons[0].center_x, self.icons[0].center_y], [money.center_x, money.center_y]) <= 20:
                    # добавление к общему счёту и счёту игры деталей, достигнувших иконку:
                    arcade.play_sound(self.coin_score, volume=0.2)
                    self.cash += 1
                    self.score += 1
                    if (not self.health_hint_marker and self.cash >= 10
                            and self.objects[0].max_hp - self.objects[0].hp >= 10):
                        self.screen_text("PRESS H TO HEAL FOR 10 DETAILS")
                        self.health_hint_marker = True
                    money.remove_from_sprite_lists()
                    self.trash.append(money)

            for gun in self.ground_lateral_weapons:
                if len(self.ground_enemies) > 0:
                    self.horizontal_lateral_weapons_fire(gun)

            if (self.frame_count + 2) % const.SPAWN_INTERVAL == 0:
                self.upgrade()

            # движение пуль:
            for enemy_bullet in self.enemy_bullet_list:
                enemy_bullet.change_y -= const.G_for_bullets  # скорость пули меняется из-за гравитации
                if (enemy_bullet.center_x - self.objects[0].center_x) ** 2 + (enemy_bullet.center_y - self.objects[0].center_y) ** 2 >= 2000 ** 2:
                    enemy_bullet.remove_from_sprite_lists()
                    self.trash.append(enemy_bullet)

            # special algorithm for sparky:
            for elem in self.sparky_bullet_list:
                for object in self.objects:
                    if abs(elem.center_x - object.center_x) < elem.width/2:
                        object.hp -= elem.size
                        elem.remove_from_sprite_lists()
                        self.trash.append(elem)

            # airstrike:
            for rocket in self.rocket_list:
                hit_list = arcade.check_for_collision_with_list(rocket, self.enemies)

                for elem in hit_list:
                    if not rocket.collision:
                        # HP removes in another part. Here comes the boom
                        self.create_boom(elem.center_x, elem.center_y, 0, 0, 3, g=0)
                        rocket.collision = True
                        elem.hp -= 20
                        arcade.play_sound(self.blast)

                if rocket.center_y - rocket.height/2 <= const.GROUND and not rocket.collision:
                    self.create_boom(rocket.center_x, rocket.center_y - rocket.height/2, 0, 0, 3, g=0)
                    rocket.collision = True
                    arcade.play_sound(self.blast)

                if rocket.collision is True:
                    circle = arcade.SpriteCircle(const.AIRSTRIKE_ROCKET_BLAST_RADIUS, arcade.color.WHITE)
                    circle.center_x = rocket.center_x
                    circle.center_y = rocket.center_y
                    hit_list = arcade.check_for_collision_with_list(circle, self.enemies)
                    for enemy in hit_list:
                        enemy.hp -= 10

                    rocket.remove_from_sprite_lists()
                    self.trash.append(rocket)
                    self.trash.append(circle)

            for sleeve in self.sleeves:
                sleeve.change_y -= const.G_for_sleeves
                if sleeve.center_y < 0:
                    # manual deleting due to "Sprite already in Spritelist" error
                    sleeve.remove_from_sprite_lists()
                    sleeve.kill()
                    del sleeve

            # day-night cycle
            if (self.frame_count + 2) % const.CYCLE == 0:
                self.cycle_number += 1
            elif self.frame_count + 2 > const.CYCLE / 255 * self.day_timer:
                self.day_timer += 1
                self.transparency += (-1)**self.cycle_number
                for background in self.backgrounds:
                    background.alpha = self.transparency
                for filter in self.color_filters:
                    filter.alpha = self.transparency

            # clouds
            for cloud in self.clouds:
                if abs(const.SCREEN_WIDTH/2 - cloud.center_x) > cloud.width + const.SCREEN_WIDTH/2:
                    cloud.remove_from_sprite_lists()
                    self.trash.append(cloud)

            # deleting of garbage
            for elem in self.trash:
                elem.remove_from_sprite_lists()
                elem.kill()
                del elem

            if self.helicopter_helicopter_indicator is False and len(self.air_enemies) >= 4:
                arcade.play_sound(self.helicopter_helicopter, volume=0.5)
                self.score += 10
                self.screen_text("HELICOPTER, HELICOPTER!")
                self.helicopter_helicopter_indicator = True

            # обновление объектов игры:
            self.clouds.update()
            self.moneys.update()
            self.enemies.update()
            self.bullet_list.update()
            self.enemy_bullet_list.update()
            self.enemy_kamikaze.update()
            self.static_objects.update()
            self.sleeves.update()
            self.booms.update()
            self.guns.update()
            self.air_enemies.update_animation(1)
            self.background.update()
            self.sparky_bullet_list.update()
            self.rocket_list.update()
            self.airmine_list.update()
            self.airgun_list.update()
            self.player_guns.update()  # code works without this one
            self.player_autoguns.update()
            self.sparkle_list.update()

        elif not self.game_over and gamemode == "started" and self.pause:
            pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """ Считывание расположения мыши игрока и изменение соответсвующих глобальных переменных """
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        """ Вызывается при нажатии мыши игроком """
        self.mouse_pressed_test = True
        if not self.game_over and gamemode == "started":
            for gun in self.player_guns:
                self.player_fire(gun)

    def on_mouse_release(self, x, y, button, modifiers):
        """ Вызывается при отпускании мыши игроком """
        self.mouse_pressed_test = False

    def on_key_press(self, symbol, modifiers):
        """ Вызывается при нажатии кнопки клавиатуры """
        global gamemode
        if gamemode == "started" and not self.pause:
            if symbol == arcade.key.KEY_1 and self.enable_gun_switching:
                for gun in self.player_guns:
                    gun.texture = arcade.load_texture("pictures/gun.png")
                    gun.fire_type = "laser"
                    gun.damage = 3
                    gun.penetra = 3
                    gun.autofire = False
                    gun.rate = 2 / const.FPS  # скорострельность
                    arcade.play_sound(self.turret_switch, volume=0.5)

            if symbol == arcade.key.KEY_2 and self.enable_gun_switching:
                for gun in self.player_guns:
                    gun.texture = arcade.load_texture("pictures/machine_gun.png")
                    gun.fire_type = "high_velocity_bullet"
                    gun.damage = 1
                    gun.penetra = 1
                    gun.autofire = True
                    gun.rate = 10 / const.FPS
                    arcade.play_sound(self.turret_switch, volume=0.5)

            if symbol == arcade.key.KEY_0 and self.enable_gun_switching:
                for gun in self.player_guns:
                    gun.texture = arcade.load_texture("pictures/initial_gun_upgraded.png")
                    gun.fire_type = "ball2"
                    gun.damage = 2
                    gun.penetra = 1
                    gun.autofire = True
                    gun.rate = 2 / const.FPS
                    arcade.play_sound(self.turret_switch, volume=0.5)

            if symbol == arcade.key.A and self.airstrike_rockets > 0:
                self.airstrike(self.airstrike_rockets)
            if symbol == arcade.key.H:
                self.heal(10)
            if symbol == arcade.key.SPACE:
                self.pause = True
            if symbol == arcade.key.I:
                pass

        elif gamemode == "started" and self.pause:
            if symbol == arcade.key.SPACE:
                self.pause = False

        elif gamemode == "lore":
            if symbol == arcade.key.SPACE:
                self.lore[0].time = const.lore_time

    def create_lore(self):
        """
        Отвечает за создание текста сюжета до начала игры
        """

        lore = arcade.Sprite(None)
        lore.time = 0
        lore.center_x = const.SCREEN_WIDTH/6
        lore.center_y = - const.SCREEN_HEIGHT/6
        lore.change_y = 1
        self.lore.append(lore)

    def fire(self, enemy):
        """
        Заставляет врага вести огонь, если оружие перезаряжено, иначе - продолжать перезаряжать оружие
        При ведении огня создаёт пулю с координатами врага
        :param enemy: враг, ведущий огонь
        """
        if enemy.recharge_time == 0:  # проверка счетчика времени перезарядки
            # specially for sparky
            if enemy.sort == "sparky":
                # unique bullet with direction
                bullet = arcade.Sprite("pictures/" + str(enemy.size) + "_bullet.png", flipped_horizontally=bool(abs(enemy.direct-1)/2))
                bullet.center_x = enemy.center_x
                bullet.center_y = enemy.center_y

                angle = math.atan2(enemy.center_y - self.objects[0].center_y,
                                   enemy.center_x - self.objects[0].center_x)

                enemy.recharge_time = -1
                bullet.size = 50

                bullet.angle = math.degrees(angle)
                bullet.change_x = - math.cos(angle) * const.BULLET_SPEED
                bullet.change_y = - math.sin(angle) * const.BULLET_SPEED

                bullet.collision = False

                self.sparky_bullet_list.append(bullet)

                enemy.change_x = - enemy.direct * const.SPARKY_SPEED * 10
                arcade.play_sound(self.sparky_shot, volume=0.5)
                enemy.texture = arcade.load_texture("pictures/sparky.png", flipped_horizontally=bool(abs(enemy.direct-1)/2))

            elif enemy.sort == "tankette" or "gun":
                bullet = arcade.Sprite("pictures/" + str(enemy.size) + "_bullet.png")
                bullet.center_x = enemy.center_x
                bullet.center_y = enemy.center_y

                angle = math.atan2(enemy.center_y - self.objects[0].center_y,
                                   enemy.center_x - self.objects[0].center_x)

                delta_angle = random.randint(-20, 20)  # разброс выстрела
                angle += delta_angle * math.pi / 180

                bullet.size = enemy.size * (2 ** const.chromium_upgrade)

                if enemy.size == 1:
                    enemy.recharge_time = 30
                elif enemy.size == 2:
                    enemy.recharge_time = 50
                elif enemy.size == 4:
                    enemy.recharge_time = 75

                bullet.angle = math.degrees(angle)
                bullet.change_x = - math.cos(angle) * const.BULLET_SPEED
                bullet.change_y = - math.sin(angle) * const.BULLET_SPEED

                self.enemy_bullet_list.append(bullet)
        else:
            enemy.recharge_time -= 1

    def player_fire(self, gun):
        """
        Осуществляет огонь и перезарядку со стороны игрока
        :param gun: пушка, которая стреляет
        """
        if gun.recharge_time <= 0 and not self.pause:
            # создание пули и помещение ее в список пуль игрока:
            angle = math.atan2(mouse_y - gun.center_y, mouse_x - gun.center_x)
            if gun.fire_type == "laser":
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
                arcade.play_sound(self.laser_sound, volume=2)
                bullet.change_x = math.cos(angle) * const.BULLET_SPEED
                bullet.change_y = math.sin(angle) * const.BULLET_SPEED
                sleeve = None
            elif gun.fire_type == "high_velocity_bullet":
                bullet = arcade.Sprite("pictures/high_velocity_bullet.png")
                bullet.change_x = math.cos(angle) * 128
                bullet.change_y = math.sin(angle) * 128
                arcade.play_sound(self.minigun_sound, volume=0.15)
                sleeve = arcade.Sprite("pictures/sleeve" + str(random.randint(1, 2)) + ".png")
                sleeve.change_x = - math.cos(angle) * 4
                sleeve.change_y = - math.sin(angle) * 4
                sleeve.change_angle = 35
            elif gun.fire_type == "ball":
                bullet = arcade.Sprite("pictures/2_bullet.png")
                bullet.change_x = math.cos(angle) * const.BULLET_SPEED
                bullet.change_y = math.sin(angle) * const.BULLET_SPEED
                arcade.play_sound(self.cannon_sound, volume=0.15)
                sleeve = arcade.Sprite("pictures/sleeve" + str(random.randint(1, 2)) + ".png")
                sleeve.change_x = - math.cos(angle) * 4
                sleeve.change_y = - math.sin(angle) * 4
                sleeve.change_angle = 20
            elif gun.fire_type == "ball2":
                bullet = arcade.Sprite("pictures/4_bullet.png")
                bullet.change_x = math.cos(angle) * const.BULLET_SPEED
                bullet.change_y = math.sin(angle) * const.BULLET_SPEED
                arcade.play_sound(self.cannon_sound, volume=0.15)
                sleeve = arcade.Sprite("pictures/sleeve.png")
                sleeve.change_x = - math.cos(angle) * 4
                sleeve.change_y = - math.sin(angle) * 4
                sleeve.change_angle = 10

                # setting up other bullet's parameters:
            bullet.fire_type = gun.fire_type
            bullet.hp = gun.penetra
            bullet.damage = gun.damage
            bullet.angle = math.degrees(angle)
            bullet.center_x = gun.center_x + math.cos(angle) * bullet.width/4
            bullet.center_y = gun.center_y + math.sin(angle) * bullet.width/4
            self.bullet_list.append(bullet)

            # setting up sleeve's parameters:
            if sleeve is not None:
                sleeve.center_x = gun.center_x
                sleeve.center_y = gun.center_y
                self.sleeves.append(sleeve)

            gun.recharge_time = 1 / gun.rate

    def horizontal_lateral_weapons_fire(self, weapon, double=True):
        """
        Заставляет горизонтальные боковые орудия вести огонь
        :param weapon: стреляющее орудие
        :param double: определяет, может ли оружие стрелять в обе стороны
        :param damage: damage
        """
        if weapon.recharge_time == 0:
            if double is True:
                for direct in [-1, 1]:
                    bullet = arcade.Sprite("pictures/4_bullet.png")
                    bullet.center_x = weapon.center_x + direct * weapon.width/2
                    bullet.center_y = weapon.center_y
                    bullet.change_x = 32 * direct
                    bullet.hp = 1
                    bullet.damage = 2 * self.lateral_weapons_damage_modifier
                    bullet.fire_type = "ball2"
                    self.bullet_list.append(bullet)
            weapon.recharge_time = 1/weapon.rate
        else:
            weapon.recharge_time -= 1

    def create_boom(self, x, y, vx, vy, type, g=1):
        """
        Создаёт взрыв и присваивает ему переменную, помогающую анимировать взрыв. Сохраняет часть скорости врага
        и меняет направление ближе к земле
        :param x: x координата центра
        :param y: y координата центра
        :param vx: проекция скорости врага на ось x
        :param vy:  проекция скорости врага на ось y
        :param type: тип взрыва, определяющий спрайт
        :param g: constant for additional velocity imitating g-force
        """
        boom = arcade.Sprite("pictures/boom" + str(type) + "_1.png", scale=1.0)
        boom.center_x = x + vx
        boom.center_y = y + vy
        boom.change_x = vx / 2
        boom.change_y = vy / 2 - g
        boom.count = const.FPB
        boom.type = type
        self.booms.append(boom)

    def default_tankette_spawn(self, size, recharge_time=0):
        """
        Создаёт танкетку
        :param size: size using for creating bullets
        :param recharge_time: initial recharge time
        """
        direct = random.choice([1, -1])
        file = "pictures/" + str(size) + const.chromium_upgrade * "chromium" + "_tankette 0 .png"
        tankette = arcade.Sprite(file, flipped_horizontally=bool(abs(direct-1)/2))
        tankette.sort = "tankette"
        tankette.file = file
        tankette.size = size
        tankette.direct = direct
        tankette.time = 0  # начальное время существования
        tankette.change_x = direct * const.TANKETTE_VELOCITIES[size - 1]
        tankette.center_x = const.SCREEN_WIDTH/2 - direct * (const.SCREEN_WIDTH/2 + tankette.width)
        tankette.bottom = const.GROUND/2
        tankette.hp = const.TANKETTE_HPS[size - 1] * (2 ** const.chromium_upgrade)  # установление HP согласно размеру
        tankette.recharge_time = recharge_time
        tankette.frame = 0
        self.ground_enemies.append(tankette)
        self.enemies.append(tankette)

    def default_drone_spawn(self, size):
        file = "pictures/" + const.chromium_upgrade * "chromium" + "drone.png"
        drone = enemies.Drone(file, self)

    def default_copter1_spawn(self, size):
        """
        Создаёт коптер
        :param size: размер
        helicopter, helicopter
        """
        direct = random.choice([1, -1])
        file = "pictures/" + str(size) + const.chromium_upgrade * "chromium" + "_copter 0 .png"
        copter = arcade.Sprite(file)
        copter.type = 1
        copter.sort = "copter"
        copter.center_x = const.SCREEN_WIDTH/2 - direct * (const.SCREEN_WIDTH/2 + copter.width)
        copter.top = random.randint(const.SCREEN_HEIGHT//2, const.SCREEN_HEIGHT - copter.height * 2)
        copter.direct = direct
        copter.file = file
        copter.size = size
        copter.hp = const.COPTER_HPS[size - 1] * (2 ** const.chromium_upgrade)
        copter.time = 0  # начальное время существования

        angle = math.atan2(self.objects[0].center_y - copter.center_y,
                           self.objects[0].center_x - copter.center_x)

        copter.change_x = const.COPTER_VELOCITY * math.cos(angle)
        copter.change_y = const.COPTER_VELOCITY * math.sin(angle)

        file = "pictures/" + const.chromium_upgrade * "chromium" + "gun1.png"
        copter.gun = arcade.Sprite(file)
        copter.gun.sort = "gun"
        copter.gun.file = file
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
        Создаёт коптер с другим поведением используя оригинальную функцию.
        Чтобы изменить поведение уже созданного объекта, работает с последним добавленным в список врагом.
        :param size: размер
        helicopter, helicopter
        """
        self.default_copter1_spawn(size)

        self.air_enemies[-1].change_x = const.COPTER_VELOCITY * self.air_enemies[-1].direct
        self.air_enemies[-1].change_y = 0

        self.air_enemies[-1].gun.change_x = self.air_enemies[-1].change_x
        self.air_enemies[-1].gun.change_y = self.air_enemies[-1].change_y
        self.air_enemies[-1].type = 2

    def default_sparky_spawn(self, size=20, recharge_time=0):
        """
        Создаёт SPARKY
        :param size: size using for creating bullets
        :param recharge_time: initial recharge time
        """
        direct = random.choice([1, -1])
        file = "pictures/20_sparky 0 .png"
        sparky = arcade.Sprite(file, flipped_horizontally=bool(abs(direct - 1) / 2))
        sparky.file = file
        sparky.sort = "sparky"
        sparky.size = size
        sparky.direct = direct
        sparky.time = 0  # начальное время существования
        sparky.change_x = direct * const.SPARKY_SPEED
        sparky.center_x = const.SCREEN_WIDTH / 2 - direct * (const.SCREEN_WIDTH / 2 + sparky.width)
        sparky.bottom = const.GROUND / 2
        sparky.hp = const.SPARKY_HP
        sparky.recharge_time = recharge_time
        sparky.frame = 0
        self.ground_enemies.append(sparky)
        self.enemies.append(sparky)
        arcade.play_sound(self.sparky_spawn, volume=0.5)

    def next_frame(self, object, frames=2):
        """
        Анимирует объект путем регулярной замены его текстуры.
        Берёт информацию о текущем кадре из имени файла
        Меняет текстуру, пересобирая имя файла с другим номером кадра
        :param object: объект с зацикленной анимацией
        :param frames: число кадров
        """
        number = int(object.file.split(" ")[1])
        if number + 1 == frames:
            number = -1
        object.file = object.file.split(" ")[0] + " " + str((number + 1) % frames) + " " + object.file.split(" ")[2]
        object.texture = self.textures[object.file][int(abs(object.direct-1)/2)]

    def spawn(self):
        """
        Увеличивает уровеень сложности, генерирует врагов в зависимости от max_enemy_points
        Большая танкетка имеет размер 4, значит, заберёт 4 очка
        Случайным образом выбирает набор врагов, суммарно по очкам не превосходящих max_enemy_points.
        Генеририует список врагов, создающихся за текущий цикл спавна
        """
        if self.spawn_timer == 0:
            self.spawn_list = []

            numbers = [0] * 21
            self.enemy_points += self.max_enemy_points
            numbers[1] = random.randint(0, self.enemy_points // (1*2))
            self.enemy_points -= numbers[1]
            numbers[4] = random.randint(0, self.enemy_points // (4*2))
            self.enemy_points -= numbers[4] * 4
            if self.enemy_points > 20 and const.chromium_upgrade == 1:
                numbers[20] = random.randint(0, 1)
                self.enemy_points -= numbers[20] * 20
            numbers[2] = self.enemy_points // 2
            self.enemy_points -= numbers[2] * 2

            for size in (1, 2, 4, 20):
                # фиксируем размер
                for elem in const.ENEMIES[size]:
                    # фиксируем тип врага фиксированного размера
                    current_number = random.randint(0, 3 * numbers[size] // 4)
                    for _ in range(current_number):
                        self.spawn_list.append([elem, size, random.randint(1, const.SPAWN_INTERVAL - 1)])
                    numbers[size] -= current_number
                if numbers[size] > 0:
                    self.spawn_list.append([const.ENEMIES[size][len(const.ENEMIES[size]) - 1],
                                            size, random.randint(0, const.SPAWN_INTERVAL)])
            self.spawn_timer = const.SPAWN_INTERVAL
            self.max_enemy_points += 3
        else:
            self.spawn_timer -= 1
            for enemy_str in self.spawn_list:
                if self.spawn_timer == enemy_str[2]:
                    eval("self.default_" + str(enemy_str[0]) + "_spawn(" + str(enemy_str[1]) + ")")

    def clouds_spawn(self):
        """
        Generates clouds from 0 to 6 every spawn_interval
        """
        if self.frame_count % const.SPAWN_INTERVAL == 0:
            self.clouds_spawn_list = []
            for _ in range(random.randint(0, 6)):
                self.clouds_spawn_list.append(random.randint(self.frame_count + 1,
                                                             self.frame_count + const.SPAWN_INTERVAL - 1))
        else:
            for elem in self.clouds_spawn_list:
                if elem == self.frame_count:
                    file = "pictures/" + const.chromium_upgrade * "chromium" + "cloud" + str(random.randint(1, 3)) + ".png"
                    cloud = arcade.Sprite(file, flipped_horizontally=random.choice([True, False]))
                    cloud.alpha = random.randint(10, 255)
                    cloud.direct = random.choice([1, -1])
                    cloud.center_x = cloud.direct * (const.SCREEN_WIDTH + cloud.width/2)
                    cloud.top = const.SCREEN_HEIGHT - random.randint(0, const.GROUND * 2)
                    cloud.change_x = - cloud.direct * random.randint(1, const.CLOUD_MAX_SPEED)
                    self.clouds.append(cloud)

    def generate_money(self, enemy):
        """
        Генерация деталей, выпадающих с поверженного врага
        :param enemy: враг
        """
        for _ in range(random.randint(0, enemy.size)):
            money = arcade.Sprite("pictures/money" + str(random.randint(1, 10)) + ".png")
            money.center_x = enemy.center_x
            money.center_y = enemy.center_y
            money.change_x = random.randint(-3, 3)
            money.change_y = random.randint(-5, 5)
            money.caught_up = False
            self.moneys.append(money)

    def heal(self, hp):
        """
        Лечение - восстановление HP дота за собранные детали
        :param hp: величина восстановления
        """
        if self.objects[0].hp + hp <= self.objects[0].max_hp and self.cash >= hp and not self.game_over:
            self.objects[0].hp += hp
            self.cash -= hp
            arcade.play_sound(self.heal_sound, volume=0.5)

    def upgrade(self):
        """
        Реализует улучшения пушки
        Обновление (согласно уровням) и вывод сопутствующего сообщения на экране
        """
        if len(const.upgrade_list_1) > 0:
            upgrade = random.choice(const.upgrade_list_1)
            const.upgrade_list_1.remove(upgrade)
            arcade.play_sound(self.upgrade_sound, volume=0.5)
            self.pause = True
            if upgrade == 0:
                lateral_weapons = arcade.Sprite("pictures/lateral_weapons.png")
                lateral_weapons.center_x = self.objects[0].center_x
                lateral_weapons.center_y = const.GROUND/2 + 32
                lateral_weapons.rate = 1 / const.FPS
                lateral_weapons.recharge_time = 30
                self.ground_lateral_weapons.append(lateral_weapons)
                self.screen_text("WEAPONS UPGRADED!\n\nAUTOMATIC GROUND WEAPONS INSTALLED")
            elif upgrade == 1:
                shield = arcade.Sprite("pictures/shield.png")
                shield.center_x = self.objects[0].center_x
                shield.bottom = self.objects[0].bottom
                self.static_objects.append(shield)
                self.objects[0].max_hp += 25
                self.objects[0].hp += 25
                self.screen_text("THE SHIELD ADDED!\n\nTHE PILLBOX IS NOW PROTECTED BY THE STEEL SHIELD")
            elif upgrade == 2:
                for gun in self.player_guns:
                    gun.texture = arcade.load_texture("pictures/initial_gun_upgraded.png")
                    gun.damage = 2
                    gun.fire_type = "ball2"
                self.screen_text("EXTENDED THE CANNON CALIBER!\n\nSHOOTS HEFTY CANNONBALLS. DAMAGE IMPROVED")
            elif upgrade == 3:
                for gun in self.player_guns:
                    gun.autofire = True
                self.screen_text("THE CANNON UPGRADED! AUTOFIRE MODE UNLOCKED:\n\nHOLD MOUSE BUTTON FOR FIRE")

        else:
            if len(const.upgrade_list_2) > 0:
                upgrade = random.choice(const.upgrade_list_2)
                const.upgrade_list_2.remove(upgrade)
                arcade.play_sound(self.upgrade_sound, volume=0.5)
                self.pause = True
                if upgrade == 0:
                    self.enable_gun_switching = True
                    self.screen_text("THE WEAPON ARSENAL REPLENISHED!\n\n"
                                     "1 TO CHOOSE THE ENERGY TURRET\n"
                                     "2 TO CHOOSE THE PRECISE MINIGUN\n"
                                     "0 TO RETURN TO THE COMMON CANNON")
                if upgrade == 1:
                    shield = arcade.Sprite("pictures/shield_modernized.png")
                    shield.center_x = self.objects[0].center_x
                    shield.bottom = self.objects[0].bottom
                    self.static_objects[0] = shield
                    self.objects[0].max_hp += 25
                    self.objects[0].hp += 25

                    # creating second turret
                    initial_gun = arcade.Sprite()
                    initial_gun.texture = self.player_guns[0].texture
                    initial_gun.center_x = const.SCREEN_WIDTH / 2
                    initial_gun.center_y = shield.height
                    initial_gun.damage = self.player_guns[0].damage
                    initial_gun.penetra = self.player_guns[0].penetra
                    initial_gun.fire_type = self.player_guns[0].fire_type
                    initial_gun.autofire = self.player_guns[0].autofire
                    initial_gun.rate = self.player_guns[0].rate
                    initial_gun.recharge_time = self.player_guns[0].recharge_time
                    self.player_guns.append(initial_gun)

                    self.screen_text("NEW TECHNOLOGIES!\n\nDUPLICATED TURRET AND AUGMENTED SHIELD")
            else:
                if len(const.upgrade_list_3) > 0:
                    upgrade = random.choice(const.upgrade_list_3)
                    const.upgrade_list_3.remove(upgrade)
                    arcade.play_sound(self.upgrade_sound, volume=0.5)
                    self.pause = True
                    if upgrade == 0:
                        self.airstrike_rockets = 4
                        self.screen_text("THE OLD MISSILES WERE REMOTELY ACCESSED."
                                         "\n\nPRESS A TO CALL AN AIRSTRIKE")
                    elif upgrade == 1:
                        self.airmines = True
                        self.screen_text("TERROR OF COPTERS!"
                                         "\n\nYOU GOT A FACTORY OF AUTOMATIC AIRMINES WORKING ON ELECTROMAGNETIC POWER"
                                         "\n\nOPERATING SYSTEM IS BASED ON RUINS OF GLOBAL IOT")
                    elif upgrade == 2:
                        self.airguns = True
                        self.airguns_spawn()
                        self.screen_text("AUTOMATIC GUIDANCE WEAPONS!"
                                         "\n\nADVANCED BATTLE CHIPS WITH COMPUTER VISION"
                                         "\nPROVIDES COMPREHENSIVE PROTECTION")
                else:
                    if const.chromium_upgrade == 0:
                        const.chromium_upgrade = 1
                        arcade.play_sound(self.thunder)
                        self.screen_text("THE SERVITUS HAS EVOLVED..."
                                         "\n\nCHROME-PLATED ARMOR TWICE AS STRONG"
                                         "\n...AND HAS A 5% CHANCE TO REFLECT BULLETS"
                                         "\n\nALSO MEET S.P.A.R.K.Y.")
                        self.pause = True
                    else:
                        if len(const.upgrade_list_4) > 0:
                            upgrade = random.choice(const.upgrade_list_4)
                            const.upgrade_list_4.remove(upgrade)
                            arcade.play_sound(self.upgrade_sound, volume=0.5)
                            self.pause = True
                            if upgrade == 0:
                                self.objects[0].max_hp += 20
                                self.objects[0].hp += 20
                                self.objects[0].texture = arcade.load_texture("pictures/pillbox_modernized.png")
                                self.static_objects[0].texture = arcade.load_texture("pictures/shield_modernized_2.png")
                                self.ground_lateral_weapons[0].texture = arcade.load_texture("pictures/lateral_weapons_modernized.png")
                                self.lateral_weapons_damage_modifier = 2
                                self.screen_text("AUGMENTED PILLBOX!"
                                                 "\n\nMAXIMUM HP. GROUND WEAPONS DAMAGE HAS BEEN DOUBLED")
                            elif upgrade == 1:
                                for gun in self.player_autoguns:
                                    gun.texture = arcade.load_texture("pictures/minigun.png")
                                    gun.fire_type = "high_velocity_mini_bullet"
                                    gun.rate = 8 / const.FPS
                                self.screen_text("FLOATING SENTRIES UPGRADED!"
                                                 "\n\nMINIGUNS HAVE INSTALLED"
                                                 "\n\nHIGH VELOCITY BULLETS INCREASE ACCURACY")
                            elif upgrade == 2:
                                self.airstrike_rockets = 8
                                self.screen_text("ACCESS TO HELLISH BOMBARDMENT!"
                                                 "\n\nAIRSTRIKE NOW CONTAINS 8 ROCKETS")
                            elif upgrade == 3:
                                self.coin_magnet = True
                                self.screen_text("MAGNET ENABLED!"
                                                 "\n\nNOW DETAILS ATTRACT TO THE PILLBOX BY MAGNETIC FORCE")
                        else:
                            if const.final_words == 0:
                                const.final_words = 1
                                self.screen_text("MAXIMUM ADVANCES. KEEP FIGHT PERSISTENTLY"
                                                 "\n\nHOLD SERVITUS AS LONG AS POSSIBLE")
                                arcade.play_sound(self.thunder)
                                self.pause = True

    def airstrike(self, rockets):
        """
        Function creates an airstrike
        :param rockets: amount of missiles falling from the sky
        """
        if self.airstrike_timer <= 0:
            for i in range(rockets):
                rocket = arcade.Sprite("pictures/rocket.png")
                rocket.center_y = (const.AIRSTRIKE_VELOCITY * 10 / const.FPS + 2 * i / rockets) * const.SCREEN_WIDTH
                rocket.change_y = - const.AIRSTRIKE_VELOCITY
                rocket.center_x = const.SCREEN_WIDTH * (i + 0.5) / rockets
                rocket.collision = False
                self.rocket_list.append(rocket)
            self.airstrike_timer = const.AIRSTRIKE_RELOAD
            arcade.play_sound(self.airstrike_calling, volume=0.8)
            arcade.play_sound(self.airstrike_inbound, volume=0.2)

    def airmines_spawn(self):
        """
        Spawns air mines
        """
        if self.airmine_timer < 0 and self.airmines:
            file = "pictures/airmine 1 .png"
            airmine = arcade.Sprite(file)
            airmine.file = file
            airmine.time = 0
            airmine.damage = 10
            airmine.center_x = self.objects[0].center_x
            airmine.center_y = self.objects[0].center_y
            airmine.y = random.randint(3 * const.GROUND, const.SCREEN_HEIGHT - const.GROUND)
            airmine.direct = random.choice([1, -1])
            if airmine.direct == 1:
                airmine.x = random.randint(2 * const.GROUND, self.objects[0].center_x - self.objects[0].width)
            else:
                airmine.x = random.randint(self.objects[0].center_x + self.objects[0].width, const.SCREEN_WIDTH - 2 * const.GROUND)

            angle = math.atan2(airmine.y - self.objects[0].center_y,
                               airmine.x - self.objects[0].center_x)
            airmine.change_x = math.cos(angle) * const.AIRMINE_SPEED
            airmine.change_y = math.sin(angle) * const.AIRMINE_SPEED
            self.airmine_list.append(airmine)

            self.airmine_timer = const.AIRMINE_SPAWN_INTERVAL
        else:
            self.airmine_timer -= 1

    def airguns_spawn(self):
        """
        Spawns automatic airships with guns
        """
        for i in range(2):
            file = "pictures/airgun 0 .png"
            airgun = arcade.Sprite(file)
            airgun.file = file
            airgun.center_x = self.objects[0].center_x + (const.SCREEN_WIDTH + const.GROUND) * (-1)**i / 4
            airgun.center_y = 1.4 * self.objects[0].height  # sets height based on pillbox height
            self.airgun_list.append(airgun)
            airgun.gun = arcade.Sprite("pictures/initial_gun.png")
            airgun.gun.center_x = airgun.center_x
            airgun.gun.center_y = airgun.center_y + airgun.height/2
            airgun.gun.damage = 1
            airgun.gun.penetra = 1
            airgun.gun.fire_type = "ball"
            airgun.gun.rate = 1 / const.FPS  # скорострельность: создаёт 1 пулю за характерное время FPS
            airgun.gun.recharge_time = const.FPS

            airgun.time = 0
            airgun.direct = 1
            self.player_autoguns.append(airgun.gun)
            arcade.play_sound(self.radar, volume=0.3)

    def autoguns_fire(self, gun):
        """
        Makes automatic player guns aim and fire
        :param gun: the exact gun
        """
        circle = arcade.SpriteCircle(300, arcade.color.WHITE)
        circle.center_x = gun.center_x
        circle.center_y = gun.center_y
        radius = (arcade.check_for_collision_with_list(circle, self.enemies))
        target = arcade.get_closest_sprite(gun, radius)

        if target is not None:
            angle = math.atan2(target[0].center_y - gun.center_y, target[0].center_x - gun.center_x)
            gun.angle = math.degrees(angle) - 90
        if gun.recharge_time <= 0 and not self.pause and target is not None:
            if gun.fire_type == "ball":
                bullet = arcade.Sprite("pictures/2_bullet.png")
                arcade.play_sound(self.cannon_sound, volume=0.15)
                bullet.change_x = math.cos(angle) * const.BULLET_SPEED
                bullet.change_y = math.sin(angle) * const.BULLET_SPEED

            elif gun.fire_type == "high_velocity_mini_bullet":
                bullet = arcade.Sprite("pictures/high_velocity_mini_bullet.png")
                arcade.play_sound(self.minigun_sound, volume=0.15)
                bullet.change_x = math.cos(angle) * 72
                bullet.change_y = math.sin(angle) * 72

            bullet.fire_type = gun.fire_type
            sleeve = arcade.Sprite("pictures/sleeve" + str(random.randint(1, 2)) + ".png")
            sleeve.change_x = - math.cos(angle) * 4
            sleeve.change_y = - math.sin(angle) * 4
            sleeve.change_angle = 25
            bullet.hp = gun.penetra
            bullet.damage = gun.damage
            bullet.angle = math.degrees(angle)
            bullet.center_x = gun.center_x + math.cos(angle) * bullet.width/4
            bullet.center_y = gun.center_y + math.sin(angle) * bullet.width/4
            self.bullet_list.append(bullet)

            # setting up sleeve's parameters:
            if sleeve is not None:
                sleeve.center_x = gun.center_x
                sleeve.center_y = gun.center_y
                self.sleeves.append(sleeve)

            gun.recharge_time = 1 / gun.rate
        elif gun.recharge_time != 0:
            gun.recharge_time -= 1

    def screen_text(self, text):
        """
        Функция, отвечающая за текущий текст по ходу игры
        :param text: текст, рисующийся на экране
        """
        self.text = text
        self.text_time = const.TEXT_TIME
