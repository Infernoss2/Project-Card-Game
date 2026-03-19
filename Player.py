from Cards import checkValue


class Player:
    def __init__(self , name):
        self.name = name
        self.hand = []
        self.face_up = []
        self.face_down = []
        self.count_cards = {}

    def take_card(self , card):
        self.hand.append(card)
        val = checkValue(card)
        if val in self.count_cards:
            self.count_cards[val] += 1
        else:
            self.count_cards[val] = 1

    def remove_card_from_hand(self , card):
        self.hand.remove(card)
        val = checkValue(card)
        self.count_cards[val] -= 1
        if self.count_cards[val] == 0:
            del self.count_cards[val]

    def remove_card_from_hand_by_index(self, index):
        card = self.hand.pop(index)
        value = checkValue(card)

        self.count_cards[value] -= 1
        if self.count_cards[value] == 0:
            del self.count_cards[value]

        return card



    def play_hand(self , index):
        card , zone = self.active_cards()
        if card is None:
            return None
        return card.pop(index)

    def show_hand(self):
        for i, card in enumerate(self.hand):
            print(f"{i}: {card}")


    def active_cards(self):
        if self.hand:
            return self.hand , "hand"
        elif self.face_up:
            return self.face_up , "face_up"
        elif self.face_down:
            return self.face_down , "face_down"
        return None , None

    def print_face_up(self):

        print(" --- ".join (str(card) for card in self.face_up))