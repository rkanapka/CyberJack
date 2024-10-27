from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from time import sleep
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
import threading
from kivy.core.audio import SoundLoader
from kivy.clock import mainthread
from core.deck import Deck
from core.player import Player


class ActiveGame(Screen):
    CURRENCY = "€$"

    deck = Deck()

    player = Player()
    player_hand_value = NumericProperty(0)
    player_balance = NumericProperty(player.balance)
    player_bet = NumericProperty(player.bet_amount)
    player_card_box = None

    opponent = Player()
    opponent_hand_value = NumericProperty(0)
    opponent_card_box = None

    status_text = ""  # winning/losing message
    current = ""  # current window
    chip_btn_text = StringProperty('')


    def betting(self, instance):  # the on_press chips function
        self.chip_btn_text = instance.text  # save the button's text
        if self.chip_btn_text == "twenty":
            self.player.bet(20)
        elif self.chip_btn_text == "fifty":
            self.player.bet(50)
        elif self.chip_btn_text == "hundred":
            self.player.bet(100)

        self.player_balance = self.player.balance
        self.player_bet = self.player.bet_amount

        SoundLoader.load("sounds/chips.mp3").play()

        self.ids.deal_btn.disabled = False  # DEAL button is enabled

    def enable_hit(self):  # If any of chips is clicked - we enable hit button
        if self.player.bet_amount != 0:
            self.ids.hit_btn.disabled = False

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
        if len(self.deck.cards) < 15:  # if there are less than 14 cards in deck, reshuffle deck
            self.deck = Deck()

        SoundLoader.load("sounds/deal_cards.wav").play()
        self.player.hand.add_card(self.deck.draw_card())
        self.player.hand.add_card(self.deck.draw_card())
        my_cards_box_widget = self.load_card_images()
        if my_cards_box_widget is not None:
            self.add_widget(my_cards_box_widget)

        self.opponent.hand.add_card(self.deck.draw_card())
        self.opponent.hand.add_card(self.deck.draw_card())

        opponent_cards_box_widget = self.load_card_images(is_opponent=True)
        if opponent_cards_box_widget is not None:
            self.add_widget(opponent_cards_box_widget)

        self.ids.hit_btn.disabled = False  # enable HIT button
        self.ids.stand_btn.disabled = False  # enable STAND button
        self.ids.deal_btn.disabled = True  # disable DEAL button
        self.ids.twenty.disabled = True  # disable 20 chip button
        self.ids.fifty.disabled = True  # disable 50 chip button
        self.ids.hundred.disabled = True  # disable 100 chip button

        self.player_hand_value = self.player.hand.value
        self.opponent_hand_value = self.opponent.hand.value

    def load_card_images(self, is_opponent=False):
        if is_opponent:
            cards_in_hand = self.opponent.hand.cards
            self.opponent_card_box, is_cards_box_reused = self.get_or_create_card_box(
                self.opponent_card_box, center_x=0.8, top=0.65, cards_in_hand=cards_in_hand
            )
            cards_box = self.opponent_card_box
        else:
            cards_in_hand = self.player.hand.cards
            self.player_card_box, is_cards_box_reused = self.get_or_create_card_box(
                self.player_card_box, center_x=0.5, top=0.45, cards_in_hand=cards_in_hand
            )
            cards_box = self.player_card_box

        for card in cards_in_hand:
            cards_box.add_widget(
                Image(
                    source=f"images/cards/{card.name}.jpg",
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
        drawn_card = self.deck.draw_card()
        self.player.hand.add_card(drawn_card)

        self.player_card_box.add_widget(
            Image(
                source=f"images/cards/{drawn_card.name}.jpg",
                size_hint_x=None,
                width=100
            )
        )
        self.player_hand_value = self.player.hand.value

        if self.player.hand.value >= 21:
            threading.Thread(target=self.check_who_won).start()
        elif self.player.hand.value > self.opponent.hand.value > 16:
            threading.Thread(target=self.stand).start()

    @mainthread
    def stand(self):
        while self.opponent.hand.value < 17:
            if self.opponent.hand.value > self.player.hand.value:
                break
            SoundLoader.load("sounds/deal_card.wav").play()
            drawn_card = self.deck.draw_card()
            self.opponent.hand.add_card(drawn_card)
            self.opponent_card_box.add_widget(
                Image(
                    source=f"images/cards/{drawn_card.name}.jpg",
                    size_hint_x=None,
                    width=100
                )
            )
            self.opponent_hand_value = self.opponent.hand.value
            sleep(1)

        if self.player.hand.value < self.opponent.hand.value < 22:
            self.status_text = "You LOST " + str(self.player.bet_amount) + f" {self.CURRENCY}!"
        else:
            self.status_text = "You WON " + str(self.player.bet_amount * 2) + f" {self.CURRENCY}!"
            self.player.balance += self.player.bet_amount * 2

        self.player_balance = self.player.balance
        self.popup(self.status_text)

    def standing(self):
        threading.Thread(target=self.stand).start()

    def check_who_won(self):
        if self.player.hand.check_for_blackjack():
            self.status_text = "You WON " + str(self.player.bet_amount * 2) + f" {self.CURRENCY}!"
            self.player.balance += self.player.bet_amount * 2
        elif self.player.hand.is_busted():
            self.status_text = "You LOST " + str(self.player.bet_amount) + f" {self.CURRENCY}!"

        self.player_balance = self.player.balance
        self.popup(self.status_text)

    def reset(self, popup):  # function called in popup function
        popup.dismiss()
        for card_box in [self.player_card_box, self.opponent_card_box]:
            card_box.clear_widgets()

        self.player.empty_hand()
        self.player_hand_value = self.player.hand.value
        self.player_bet = self.player.bet_amount

        self.opponent.empty_hand()
        self.opponent_hand_value = self. opponent.hand.value

        self.ids.twenty.disabled = False  # enable 20 chip button
        self.ids.fifty.disabled = False  # enable 50 chip button
        self.ids.hundred.disabled = False  # enable 100 chip button
        self.ids.hit_btn.disabled = True  # disable HIT button
        self.ids.stand_btn.disabled = True  # disable STAND button
