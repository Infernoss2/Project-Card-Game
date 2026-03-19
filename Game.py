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
                player.take_card(self.current_deck.draw_card())


    def checkIfBurn(self):
        if len(self.current_pile) >= 4:
            if self.current_pile[0] == self.current_pile[1] == self.current_pile[2] == self.current_pile[3]:
                print("the pile is burned , another turn")
                return True
        if checkValue(self.current_pile[len(self.current_pile)-1]) == 8:
            print("the pile is burned , another turn")
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
            chosen_cards.append(player.remove_card_from_hand_by_index(index))

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
                    player.hand.take_card(card)
                    self.current_pile.clear()

            except (ValueError, IndexError):
                print("invalid input.")
            return

        elif zone == "face_up":
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

        elif zone == "hand":
            has_valid_card = False
            for card in cards:
                if isValidCard(self.current_pile, card):
                    has_valid_card = True
                    break
            if not has_valid_card and len(self.current_pile) > 0:
                print(f"{player.name} has no valid card. picking up the pile.")
                for card in self.current_pile:
                    player.take_card(card)
                self.current_pile.clear()
                return

            turn_complete = False
            while not turn_complete:
                try:
                    for i, card in enumerate(cards):
                        print(f"{i}: {card}")
                    choice = int(input("Pick a card index: "))
                    chosen_card = player.hand[choice]
                    value = checkValue(chosen_card)
                    count = player.count_cards[value]

                    amount = 1
                    if count > 1:
                        amount = int(input(f"You have {count} cards of value {value}. How many do you want to play ? "))
                        if amount < 1 or amount > count:
                            print("invalid amount.")
                            continue

                    cards_to_play = []
                    for card in player.hand:
                        if checkValue(card) == value and len(cards_to_play) < amount:
                            cards_to_play.append(card)

                    if isValidCard(self.current_pile, cards_to_play[0]):
                        for card in cards_to_play:
                            player.remove_card_from_hand(card)
                            self.current_pile.append(card)

                        print("Great move!")
                        print("played cards:")
                        for card in cards_to_play:
                            print(card)

                        if self.checkIfBurn():
                            self.trash.extend(self.current_pile)
                            self.current_pile.clear()
                            turn_complete = False
                        else:
                            turn_complete = True
                    else:
                        if len(self.current_pile) > 0:
                            print(f"Not a valid card, try again. card on top is {self.current_pile[-1]}")
                        else:
                            print("Not a valid card, try again.")

                except (ValueError, IndexError):
                    print("Invalid input. Please enter a valid number.")

        if zone == "hand":
            while len(player.hand) < 3 and len(self.current_deck.deck) > 0:
                player.take_card(self.current_deck.draw_card())

            print(f"{len(self.current_deck.deck)} cards left.")














