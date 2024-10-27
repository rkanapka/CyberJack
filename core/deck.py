from core.card import Card
from random import shuffle


RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]  # ...Jacks, Queens, Kings, Aces
SUITS = ["S", "H", "C", "D"]  # Spades, Hearts, Clubs, Diamonds

class Deck:
    def __init__(self):
        self.cards = self._make_deck()
        self._shuffle()

    @staticmethod
    def _make_deck():
        return [Card(rank=RANKS[i % 13], suit=SUITS[int(i / 13)]) for i in range(0, 52)]

    def _shuffle(self):
        shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None
