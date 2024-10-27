from kivy.app import App
from kivy.uix.screenmanager import FadeTransition, ScreenManager
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

from screens.main_menu import MainMenu
from screens.active_game import ActiveGame


kv = Builder.load_file("main.kv")


class ImageButton(ButtonBehavior, Image):  # class for making clickable image
    pass

class WindowManager(ScreenManager):
    pass

class CyberJack(App):
    def build(self):
        self.icon = 'images/chip.ico'
        wm = WindowManager(transition=FadeTransition())

        screens = [MainMenu(name="main"), ActiveGame(name="playing")]
        for screen in screens:
            wm.add_widget(screen)

        wm.current = "main"
        return wm

if __name__ == "__main__":
    CyberJack().run()
