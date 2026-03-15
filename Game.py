from pyparsing import empty

from Cards import Deck, isValidCard
from Player import Player

class Game:
    def __init__(self):
        self.current_deck = Deck()
        self.Players = []
        self.current_pile = []
        self.current_player = 0

    def add_player(self, name):
        player = Player(name)
        self.Players.append(player)

    def deal_cards(self):
        for player in self.Players:
            for _ in range(3):
                player.face_down.append(self.current_deck.draw_card())
            for _ in range(6):
                player.hand.append(self.current_deck.draw_card())

    def checkIfBurn(self):
        if len(self.current_deck.deck) >= 4:
            if self.current_deck.deck[0] == self.current_deck.deck[1] == self.current_deck.deck[2] == self.current_deck.deck[3]:
                return True
            else:
                return False
        return False


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


    def play_turn(self,player):
        has_valid_card = False
        for card in player.hand:
            if isValidCard(self.current_pile, card):
                has_valid_card = True
                break
        if not has_valid_card and len(self.current_pile) > 0:
            print(f"\n{player.name} has no valid cards! Picking up the pile.")
            player.hand.extend(self.current_pile)

            self.current_pile.clear()
            return


        turn_complete = False
        while not turn_complete:
            player.show_hand()
            try:
                choice = int(input("Pick a card index: "))
                card = player.hand[choice]

                if isValidCard(self.current_pile, card):
                    self.current_pile.append(player.hand.pop(choice))  # מוציא מהיד ושם בערימה
                    print("Great move!")
                    print(f"played card: {card}")


                    if self.checkIfBurn():
                        pass
                    else:
                        turn_complete = True
                else:
                    print("Not a valid card, try again.")

            except (ValueError, IndexError):
                print("Invalid input. Please enter a valid number.")

        # משיכת קלפים אם צריך
        if len(player.hand) < 3 and len(self.current_deck.deck) > 0:
            player.hand.append(self.current_deck.draw_card())







