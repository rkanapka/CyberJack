from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from random import shuffle
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from time import sleep
from kivy.uix.floatlayout import FloatLayout
import threading
from kivy.core.audio import SoundLoader
from kivy.clock import mainthread


class MainMenu(Screen):
    pass


class PlayGame(Screen):
    left_money = NumericProperty(1000)
    your_bet = NumericProperty(0)
    your_hand = StringProperty("")
    y_hand = []
    sum_of_hand = NumericProperty(0)

    dealer_hand = StringProperty("")
    d_hand = []
    sum_dealer = NumericProperty(0)

    status_text = ""  # winning/losing message
    current = ""  # current window
    chip_btn_text = StringProperty('')

    suit = ["S", "H", "C", "D"]  # Spades, Hearts, Clubs, Diamonds
    card = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "D", "K", "A"]
    deck = []

    def make_deck(self):
        self.deck = []
        for i in range(0, 52):  # making deck
            self.deck.append(self.card[i % 13] + self.suit[int(i / 13)])

        shuffle(self.deck)  # shuffling deck

    def betting(self, instance):  # the on_press chips function
        self.chip_btn_text = instance.text  # save the button's text
        if self.chip_btn_text == "twenty":
            if self.your_bet + 20 <= 300 and self.left_money >= 20:
                self.left_money -= 20
                self.your_bet += 20
        elif self.chip_btn_text == "fifty":
            if self.your_bet + 50 <= 300 and self.left_money >= 50:
                self.left_money -= 50
                self.your_bet += 50
        elif self.chip_btn_text == "hundred":
            if self.your_bet + 100 <= 300 and self.left_money >= 100:
                self.left_money -= 100
                self.your_bet += 100

        SoundLoader.load("sounds/chips.mp3").play()

        self.ids.deal_btn.disabled = False  # DEAL button is enabled

    def enable_hit(self):  # If any of chips is clicked - we enable hit button
        if self.your_bet != 0:
            self.ids.hit_btn.disabled = False

    @staticmethod
    def total_sum(arg1, arg2, arg3):
        arg1 = 0
        arg2 = arg3.split()
        # TODO A value can be 1 or 10. ATM I set it to 10
        for i in arg2:  # calculating sum of hand
            if i[0] == "J" or i[0] == "D" or i[0] == "K" or i[0] == "A" or i[0] == "1":
                arg1 += 10
            else:
                arg1 += int(i[0])

        return arg1  # sum of cards value returned here

    @mainthread
    def popup(self, arg1):  # arg1 is popup message
        sleep(1)
        fl = FloatLayout()
        fl.add_widget(Label(text=arg1, pos_hint={'x': 0, 'center_y': 0.95}))
        popup = Popup(title="", separator_height=0, title_size=10, content=fl,
                      size_hint=(None, None), size=(300, 100),
                      auto_dismiss=False, pos_hint={'x': 0.3, 'center_y': 0.48})
        but = Button(text="Go on", on_press=popup.dismiss, pos_hint={'x': 0.12, 'center_y': 0.48}, size_hint=(0.8, 0.2))
        but.bind(on_press=lambda x: self.reset())
        fl.add_widget(but)
        popup.open()

    def deal_cards(self, *args):
        if len(self.deck) < 15:  # if there are less than 14 cards in deck, reshuffle deck
            self.make_deck()

        SoundLoader.load("sounds/deal_cards.wav").play()
        self.your_hand = self.deck[0] + " " + self.deck[1]
        self.dealer_hand = self.deck[2] + " " + self.deck[3]

        for i in range(4):
            self.deck.remove(self.deck[0])  # delete dealt cards from the deck

        self.ids.hit_btn.disabled = False  # enable HIT button
        self.ids.stand_btn.disabled = False  # enable STAND button
        self.ids.deal_btn.disabled = True  # disable DEAL button
        self.ids.twenty.disabled = True  # disable 20 chip button
        self.ids.fifty.disabled = True  # disable 50 chip button
        self.ids.hundred.disabled = True  # disable 100 chip button

        self.sum_of_hand = self.total_sum(self.sum_of_hand, self.y_hand, self.your_hand)
        self.sum_dealer = self.total_sum(self.sum_dealer, self.d_hand, self.dealer_hand)

    def hit_card(self):
        SoundLoader.load("sounds/deal_card.wav").play()
        self.your_hand += " " + self.deck[0]
        del self.deck[0]  # delete "first" card of the deck

        # sum of cards value again, because we draw 1 more card
        self.sum_of_hand = self.total_sum(self.sum_of_hand, self.y_hand, self.your_hand)

        if self.sum_of_hand >= 21:
            threading.Thread(target=self.check_who_won).start()
        elif self.sum_of_hand > self.sum_dealer > 16:
            threading.Thread(target=self.stand).start()

    def stand(self):
        while self.sum_dealer < 17:
            if self.sum_dealer < self.sum_of_hand:
                SoundLoader.load("sounds/deal_card.wav").play()
                self.dealer_hand += " " + self.deck[0]
                del self.deck[0]  # delete "first" card of the deck
                self.sum_dealer = self.total_sum(self.sum_dealer, self.d_hand, self.dealer_hand)
                sleep(1)
            else:
                break

        if self.sum_of_hand < self.sum_dealer < 22:
            self.status_text = "You LOST " + str(self.your_bet) + " Eur!"
        else:
            self.status_text = "You WON " + str(self.your_bet * 2) + " Eur!"
            self.left_money += self.your_bet * 2

        self.popup(self.status_text)

    def standing(self):
        threading.Thread(target=self.stand).start()

    def check_who_won(self):
        if self.sum_of_hand == 21:
            self.status_text = "You WON " + str(self.your_bet * 2) + " Eur!"
            self.left_money += self.your_bet * 2
        elif self.sum_of_hand > 21:
            self.status_text = "You LOST " + str(self.your_bet) + " Eur!"

        self.popup(self.status_text)

    def reset(self):  # function called in popup function
        self.your_bet = 0
        self.sum_of_hand = 0
        self.your_hand = ""
        self.y_hand = []

        self.sum_dealer = 0
        self.d_hand = []
        self.dealer_hand = ""

        self.ids.twenty.disabled = False  # enable 20 chip button
        self.ids.fifty.disabled = False  # enable 50 chip button
        self.ids.hundred.disabled = False  # enable 100 chip button
        self.ids.hit_btn.disabled = True  # disable HIT button
        self.ids.stand_btn.disabled = True  # disable STAND button


class ImageButton(ButtonBehavior, Image):  # class for making clickable image
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("blackjack.kv")

sm = WindowManager()

screens = [MainMenu(name="main"), PlayGame(name="playing")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "main"


class BlackJack(App):
    def build(self):
        self.icon = 'images/chip.ico'
        return sm


if __name__ == "__main__":
    BlackJack().run()
