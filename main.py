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
from kivy.uix.boxlayout import BoxLayout
import threading
from kivy.core.audio import SoundLoader
from kivy.clock import mainthread


class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        SoundLoader.load('sounds/main_menu.mp3').play()
        #  TODO stop sound on Play button press


class PlayGame(Screen):
    CURRENCY = "€$"

    my_card_box = None

    left_money = NumericProperty(1000)
    your_bet = NumericProperty(0)
    your_hand = []
    sum_of_hand = NumericProperty(0)

    opponent_card_box = None
    opponent_hand = []
    sum_opponent = NumericProperty(0)

    status_text = ""  # winning/losing message
    current = ""  # current window
    chip_btn_text = StringProperty('')

    suit = ["S", "H", "C", "D"]  # Spades, Hearts, Clubs, Diamonds
    card = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
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
    def total_sum(cards_in_hand):
        """
        Calculate total value of cards in hand.

        For each Ace, we initially add 1 to the total value. If the total is below 12,
        we can treat one Ace as 11 instead of 1, so we add an additional 10 to the total.

        :param cards_in_hand: list of cards in hand e.g. ['2S', 'AA']
        :return: total value of cards.
        """
        total = 0
        aces_exists = False
        for card_name in cards_in_hand:  # calculating sum of hand
            if card_name[0] in ["J", "Q", "K"]:
                total += 10
            elif card_name[0] == "A":
                total += 1
                aces_exists = True
            else:
                total += int(card_name[0])

        if aces_exists and total < 12:
            total += 10

        return total  # sum of cards value returned here

    @mainthread
    def popup(self, text):
        sleep(1)
        fl = FloatLayout()
        fl.add_widget(Label(text=text, pos_hint={'x': 0, 'center_y': 0.95}))
        popup = Popup(title="", separator_height=0, title_size=10, content=fl,
                      size_hint=(None, None), size=(300, 100),
                      auto_dismiss=False, pos_hint={'x': 0.3, 'center_y': 0.48})
        but = Button(
            text="Go on",
            pos_hint={'x': 0.12, 'center_y': 0.48},
            size_hint=(0.8, 0.2)
        )
        but.bind(on_press=lambda x: self.reset(popup))
        fl.add_widget(but)
        popup.open()

    def deal_cards(self, *args):
        if len(self.deck) < 15:  # if there are less than 14 cards in deck, reshuffle deck
            self.make_deck()

        SoundLoader.load("sounds/deal_cards.wav").play()
        self.your_hand.extend(self.deck[:2])
        my_cards_box_widget = self.load_card_images(self.your_hand)
        if my_cards_box_widget is not None:
            self.add_widget(my_cards_box_widget)
        
        self.opponent_hand.extend(self.deck[2:4])
        opponent_cards_box_widget = self.load_card_images(self.opponent_hand, is_opponent=True)
        if opponent_cards_box_widget is not None:
            self.add_widget(opponent_cards_box_widget)

        del self.deck[:5]  # delete dealt cards from the deck

        self.ids.hit_btn.disabled = False  # enable HIT button
        self.ids.stand_btn.disabled = False  # enable STAND button
        self.ids.deal_btn.disabled = True  # disable DEAL button
        self.ids.twenty.disabled = True  # disable 20 chip button
        self.ids.fifty.disabled = True  # disable 50 chip button
        self.ids.hundred.disabled = True  # disable 100 chip button

        self.sum_of_hand = self.total_sum(self.your_hand)
        self.sum_opponent = self.total_sum(self.opponent_hand)

    def load_card_images(self, cards_in_hand, is_opponent=False):
        if is_opponent:
            self.opponent_card_box, is_cards_box_reused = self.get_or_create_card_box(
                self.opponent_card_box, center_x=0.8, top=0.65, cards_in_hand=cards_in_hand
            )
            cards_box = self.opponent_card_box
        else:
            self.my_card_box, is_cards_box_reused = self.get_or_create_card_box(
                self.my_card_box, center_x=0.5, top=0.45, cards_in_hand=cards_in_hand
            )
            cards_box = self.my_card_box

        for card_name in cards_in_hand:
            cards_box.add_widget(
                Image(
                    source=f"images/cards/{card_name}.jpg",
                    size_hint_x=None,
                    width=100
                )
            )
        if is_cards_box_reused:
            return None
        return cards_box

    @staticmethod
    def get_or_create_card_box(existing_box, center_x, top, cards_in_hand):
        if existing_box:
            return existing_box, True
        spacing = 5
        return BoxLayout(
            size_hint=(None, 0.2),
            pos_hint={'center_x': center_x, 'top': top},
            width=len(cards_in_hand) * 100 + (len(cards_in_hand) - 1) * spacing,
            spacing=spacing
        ), False

    def hit_card(self):
        SoundLoader.load("sounds/deal_card.wav").play()
        self.your_hand.append(self.deck[0])

        self.my_card_box.add_widget(
                Image(
                    source=f"images/cards/{self.deck[0]}.jpg",
                    size_hint_x=None,
                    width=100
                )
            )
        del self.deck[0]  # delete "first" card of the deck

        # sum of cards value again, because we draw 1 more card
        self.sum_of_hand = self.total_sum(self.your_hand)

        if self.sum_of_hand >= 21:
            threading.Thread(target=self.check_who_won).start()
        elif self.sum_of_hand > self.sum_opponent > 16:
            threading.Thread(target=self.stand).start()

    @mainthread
    def stand(self):
        while self.sum_opponent < 17:
            if self.sum_opponent < self.sum_of_hand:
                SoundLoader.load("sounds/deal_card.wav").play()
                self.opponent_hand.append(self.deck[0])
                self.opponent_card_box.add_widget(
                    Image(
                        source=f"images/cards/{self.deck[0]}.jpg",
                        size_hint_x=None,
                        width=100
                    )
                )
                del self.deck[0]  # delete "first" card of the deck
                self.sum_opponent = self.total_sum(self.opponent_hand)
                sleep(1)
            else:
                break

        if self.sum_of_hand < self.sum_opponent < 22:
            self.status_text = "You LOST " + str(self.your_bet) + f" {self.CURRENCY}!"
        else:
            self.status_text = "You WON " + str(self.your_bet * 2) + f" {self.CURRENCY}!"
            self.left_money += self.your_bet * 2

        self.popup(self.status_text)

    def standing(self):
        threading.Thread(target=self.stand).start()

    def check_who_won(self):
        if self.sum_of_hand == 21:
            self.status_text = "You WON " + str(self.your_bet * 2) + f" {self.CURRENCY}!"
            self.left_money += self.your_bet * 2
        elif self.sum_of_hand > 21:
            self.status_text = "You LOST " + str(self.your_bet) + f" {self.CURRENCY}!"

        self.popup(self.status_text)

    def reset(self, popup):  # function called in popup function
        popup.dismiss()
        for card_box in [self.my_card_box, self.opponent_card_box]:
            card_box.clear_widgets()

        self.your_bet = 0
        self.sum_of_hand = 0
        self.your_hand = []

        self.sum_opponent = 0
        self.opponent_hand = []

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
