from core.hand import Hand


ROUND_BET_LIMIT = 300


class Player:
    def __init__(self):
        self.balance = 1000
        self.bet_amount = 0
        self.hand = Hand()

    def bet(self, amount):
        if self.bet_amount + amount <= ROUND_BET_LIMIT and self.balance >= amount:
            self.bet_amount += amount
            self.balance -= amount

    def empty_hand(self):
        self.hand = Hand()
        self.bet_amount = 0