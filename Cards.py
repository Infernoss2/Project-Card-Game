import random
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

VALUES = ["A", "2", "3", "4", "5", "6", "7",
          "8", "9", "10", "J", "Q", "K"]


class Card:
    def __init__(self ,suit ,value):
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.value} of {self.suit}"


class Deck:
    def __init__(self):
        self.deck = []
        for suit in SUITS:
            for value in VALUES:
                self.deck.append(Card(suit, value))

    def shuffle(self):
        random.shuffle(self.deck)

    def draw_card(self):
        return self.deck.pop()

def isValidCard(pile, card):
    pass