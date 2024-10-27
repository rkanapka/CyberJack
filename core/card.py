class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = self._calculate_value()
        self.name = self.rank + self.suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def _calculate_value(self):
        if self.rank in ["J", "Q", "K"]:
            value = 10
        elif self.rank == "A":
            # May be adjusted to 1 based on total sum
            value = 11
        else:
            value = int(self.rank)
        return value
