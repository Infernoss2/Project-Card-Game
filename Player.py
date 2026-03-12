class Player:
    def __init__(self , name):
        self.name = name
        self.hand = []
        self.face_up = []
        self.face_down = []

    def take_card(self , card):
        self.hand.append(card)

    def play_hand(self , index):
        self.hand.pop(index)

    def show_hand(self):
        for i, card in enumerate(self.hand):
            print(f"{i}: {card}")

