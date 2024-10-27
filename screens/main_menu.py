from kivy.uix.screenmanager import Screen
from kivy.core.audio import SoundLoader


class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_menu_sound = SoundLoader.load('sounds/main_menu.mp3')
        self.main_menu_sound.play()

        self.active_game_sound = SoundLoader.load('sounds/hyper-spoiler_cyberpunk_2077_ost.mp3')
