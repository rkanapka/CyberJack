from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

from screens.main_menu import MainMenu
from screens.active_game import ActiveGame


class ImageButton(ButtonBehavior, Image):  # class for making clickable image
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("main.kv")

sm = WindowManager()

screens = [MainMenu(name="main"), ActiveGame(name="playing")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "main"


class CyberJack(App):
    def build(self):
        self.icon = 'images/chip.ico'
        return sm


if __name__ == "__main__":
    CyberJack().run()
