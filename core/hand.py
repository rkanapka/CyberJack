class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces_count = 0

    def __str__(self):
        cards_str = ', '.join(str(card) for card in self.cards)
        return f"Hand: {cards_str} | Value: {self.value}"

    def add_card(self, card):
        self.cards.append(card)
        self.value += card.value

        if card.rank == "A":
            self._adjust_for_aces()

    def _adjust_for_aces(self):
        """Adjusts the hand's value if there are aces and the total value exceeds 21."""
        while self.value > 21 and self.aces_count:
            self.value -= 10
            self.aces_count -= 1

    def check_for_blackjack(self):
        return self.value == 21

    def is_busted(self):
        return self.value > 21
