from random import choice

from pyparsing import empty

from Cards import Deck, isValidCard, checkValue
from Player import Player

class Game:
    def __init__(self):
        self.current_deck = Deck()
        self.Players = []
        self.current_pile = []
        self.current_player = 0
        self.trash = []

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
            elif checkValue(self.current_pile[len(self.current_pile)-1]) == 8:
                return True
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



    def play_turn(self, player):
        cards, zone = player.active_cards()

        if cards is None:
            print(f"{player.name}, you have no cards left.")
            return

        if zone == "face_down":
            try:
                for i, card in enumerate(cards):
                    print(f"{i}: [hidden]")

                choice = int(input("pick a card, good luck: "))
                card = player.play_hand(choice)

                print(f"you picked {card}.")

                if isValidCard(self.current_pile, card):
                    self.current_pile.append(card)
                    print("so lucky !")



                else:
                    print("sorry , bad luck !")
                    player.hand.extend(self.current_pile)
                    player.hand.append(card)
                    self.current_pile.clear()

            except (ValueError, IndexError):
                print("invalid input.")
            return

        elif zone == "face_up" or zone == "hand":
            has_valid_card = False
            for card in cards:
                if isValidCard(self.current_pile, card):
                    has_valid_card = True
                    break

            if not has_valid_card and len(self.current_pile) > 0:
                print(f"{player.name} has no valid card. picking up the pile.")
                player.hand.extend(self.current_pile)
                self.current_pile.clear()
                return

            turn_complete = False

            while not turn_complete:
                try:
                    for i, card in enumerate(cards):
                        print(f"{i}: {card}")

                    choice = int(input("Pick a card index: "))
                    card = cards[choice]

                    if isValidCard(self.current_pile, card):
                        played_card = player.play_hand(choice)
                        self.current_pile.append(played_card)

                        print("Great move!")
                        print(f"played card: {played_card}")

                        if self.checkIfBurn():
                            self.trash.extend(self.current_pile)
                            self.current_pile.clear()
                            if len(self.current_deck.deck) > 0:
                                player.hand.append(self.current_deck.draw_card())
                            turn_complete = False

                            cards, zone = player.active_cards()
                            if cards is None:
                                return
                        else:
                            turn_complete = True
                    else:
                        print(f"Not a valid card, try again, card on top is {self.current_pile[len(self.current_pile)-1]}")

                except (ValueError, IndexError):
                    print("Invalid input. Please enter a valid number.")

        if zone == "hand":
            while len(player.hand) < 3 and len(self.current_deck.deck) > 0:
                player.hand.append(self.current_deck.draw_card())

            print(f"{len(self.current_deck.deck)} cards left.")














