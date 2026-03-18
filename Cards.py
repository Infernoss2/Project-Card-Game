import random
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

VALUES = ["2", "3", "4", "5", "6", "7",
          "8", "9", "10", "J", "Q", "K" ,"A"]


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


def checkValue(card):
    return VALUES.index(card.value)


def isValidCard(pile, card):
    my_card_val = checkValue(card)

    if len(pile) == 0:
        return True

    last_card = pile[-1]
    last_card_val = checkValue(last_card)

    if last_card_val == 1 and len(pile) >= 1:
        last_card = pile[-2]
        last_card_val = checkValue(last_card)


    if my_card_val in [0,1,8] and last_card_val != 10:
        return True


    elif last_card_val == 5:
        if my_card_val in [0,1,8] or my_card_val <= 5:
            return True
        else:
            return False

    elif my_card_val >= last_card_val != 5:
        return True


    return False










