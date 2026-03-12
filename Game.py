from Cards import Deck
from Player import Player

class Game:
    def __init__(self):
        self.deck = Deck()
        self.Players = []
        self.discards_pile = []
        self.current_player = 0

    def add_player(self, name):
        player = Player(name)
        self.Players.append(player)

    def deal_cards(self):
        for player in self.Players:
            for _ in range(3):
                player.face_down.append(self.deck.draw_card())
            for _ in range(6):
                player.hand.append(self.deck.draw_card())




    def choose_face_up_cards(self, player):
        print(f"\n{player.name}, choose 3 face-up cards.")

        while True:
            print("\nYour hand:")
            player.show_hand()

            choice = input("Enter 3 different indices separated by spaces: ")

            parts = choice.split()

            if len(parts) != 3:
                print("You must enter exactly 3 numbers.")
                continue

            try:
                indices = list(map(int, parts))
            except ValueError:
                print("Please enter only numbers.")
                continue

            if len(set(indices)) != 3:
                print("You must choose 3 different cards.")
                continue

            valid = True
            for index in indices:
                if index < 0 or index >= len(player.hand):
                    valid = False
                    break

            if not valid:
                print("One or more indices are invalid.")
                continue

            break

        chosen_cards = []

        for index in sorted(indices, reverse=True):
            chosen_cards.append(player.hand.pop(index))

        chosen_cards.reverse()

        for card in chosen_cards:
            player.face_up.append(card)


