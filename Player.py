


class Player:
    def __init__(self , name):
        self.name = name
        self.hand = []
        self.face_up = []
        self.face_down = []

    def take_card(self , card):
        self.hand.append(card)

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

        print(" -- ".join(str(card) for card in self.face_up))