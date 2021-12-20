import mygame
import constants as const


def main():
    """ Главная функция """
    window = mygame.MyGame(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, const.SCREEN_TITLE)
    window.setup()
    mygame.arcade.run()


if __name__ == "__main__":
    main()
