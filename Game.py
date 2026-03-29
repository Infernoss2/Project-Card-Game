from Cards import Deck, isValidCard, checkValue
from Player import Player


class Game:
    def __init__(self):
        self.current_deck = Deck()
        self.Players = []
        self.current_pile = []
        self.current_player = 0
        self.trash = []
        self.finish_order = []

        # מצבי משחק
        self.state = "setup"          # setup / playing / game_over
        self.setup_player_index = 0   # מי בוחר עכשיו 3 קלפים face-up
        self.selected_indices = []    # בחירות זמניות בזמן setup

    def add_player(self, name):
        self.Players.append(Player(name))

    def deal_cards(self):
        self.current_deck.shuffle()

        for player in self.Players:
            for _ in range(3):
                player.face_down.append(self.current_deck.draw_card())

            for _ in range(6):
                player.take_card(self.current_deck.draw_card())


    def get_current_player(self):
        if not self.Players:
            return None
        return self.Players[self.current_player]

    def get_setup_player(self):
        if self.setup_player_index >= len(self.Players):
            return None
        return self.Players[self.setup_player_index]

    def refill_hand(self, player):
        while len(player.hand) < 3 and len(self.current_deck.deck) > 0:
            player.take_card(self.current_deck.draw_card())

    def pickup_pile(self, player):
        for card in self.current_pile:
            player.take_card(card)
        self.current_pile.clear()

    def remove_finished_players(self):
        removed_current = False
        i = 0

        while i < len(self.Players):
            player = self.Players[i]
            if len(player.hand) == 0 and len(player.face_up) == 0 and len(player.face_down) == 0:
                if i < self.current_player:
                    self.current_player -= 1
                elif i == self.current_player:
                    removed_current = True

                self.finish_order.append(player.name)
                self.Players.pop(i)
            else:
                i += 1

        if len(self.Players) <= 1:
            self.state = "game_over"
            self.current_player = 0
            if len(self.Players) == 1:
                self.finish_order.append(self.Players[0].name)
            return

        if removed_current:
            self.current_player %= len(self.Players)

    def advance_turn(self , steps = 1):
        self.remove_finished_players()

        if self.state == "game_over":
            return

        self.current_player = (self.current_player + steps) % len(self.Players)

    # -----------------------------
    # בדיקות pile / burn
    # -----------------------------
    def check_if_burn(self):
        # לפי החוקים שלך כרגע: 8 שורף
        if len(self.current_pile) > 0 and checkValue(self.current_pile[-1]) == 8:
            return True

        # 4 עליונים מאותו ערך שורפים
        if len(self.current_pile) >= 4:
            last_four = self.current_pile[-4:]
            values = [checkValue(card) for card in last_four]
            if values[0] == values[1] == values[2] == values[3]:
                return True

        return False

    def burn_pile(self):
        self.trash.extend(self.current_pile)
        self.current_pile.clear()

    def can_player_play_any(self, player):
        cards, zone = player.active_cards()
        if cards is None:
            return False

        if zone == "face_down":
            return True

        for card in cards:
            if isValidCard(self.current_pile, card):
                return True

        return False

    # -----------------------------
    # setup: בחירת 3 קלפים face-up
    # -----------------------------
    def toggle_setup_card(self, index):
        if self.state != "setup":
            return False, "Setup is over."

        player = self.get_setup_player()
        if player is None:
            return False, "No setup player."

        if index < 0 or index >= len(player.hand):
            return False, "Invalid card index."

        if index in self.selected_indices:
            self.selected_indices.remove(index)
            return True, "Card unselected."

        if len(self.selected_indices) >= 3:
            return False, "You can choose only 3 cards."

        self.selected_indices.append(index)
        return True, f"Selected {len(self.selected_indices)}/3"

    def confirm_setup_selection(self):
        if self.state != "setup":
            return False, "Setup is over."

        player = self.get_setup_player()
        if player is None:
            return False, "No setup player."

        if len(self.selected_indices) != 3:
            return False, "You must choose exactly 3 cards."

        chosen_cards = []
        for index in sorted(self.selected_indices, reverse=True):
            chosen_cards.append(player.remove_card_from_hand_by_index(index))

        chosen_cards.reverse()
        player.face_up.extend(chosen_cards)

        self.selected_indices.clear()
        self.setup_player_index += 1

        if self.setup_player_index >= len(self.Players):
            self.state = "playing"
            self.current_player = 0
            return True, "Setup finished. Game starts."

        next_player = self.get_setup_player()
        return True, f"{next_player.name}, choose 3 face-up cards."

    # -----------------------------
    # קליקים מה-GUI
    # -----------------------------
    def handle_card_click(self, zone, index):
        if self.state == "setup":
            player = self.get_setup_player()
        else:
            player = self.get_current_player()
        if player is None:
            return False, "No current player."

        if self.state == "setup":
            if zone != "hand":
                return False, "In setup, you can only choose from hand."

            if index < 0 or index >= len(player.hand):
                return False, "Invalid card index."

            if index in self.selected_indices:
                self.selected_indices.remove(index)
                return True, f"Unselected card {player.hand[index]}."

            if len(self.selected_indices) >= 3:
                return False, "You can only choose 3 cards."

            self.selected_indices.append(index)
            return True, f"Selected card {player.hand[index]}."

        if self.state == "playing":
            cards, active_zone = player.active_cards()

            if zone != active_zone:
                return False, "You can only play from the active zone."

            if zone == "face_down":
                return self.play_face_down_card(player, index)

            return False, "Use selection and confirm for hand or face up."

        return False, "Invalid game state."


    def play_selected_cards(self, zone, indices):
        player = self.get_current_player()
        if player is None:
            return False, "No current player."

        if not indices:
            return False, "No cards selected."

        if zone == "hand":
            return self.play_hand_card(player, indices)

        if zone == "face_up":
            return self.play_face_up_card(player, indices)

        return False, "Invalid zone."



    # -----------------------------
    # מהלכים לפי אזור
    # -----------------------------
    def play_hand_card(self, player, indices):
        for i in indices:
            if i < 0 or i >= len(player.hand):
                return False, "Invalid card index."

        cards = [player.hand[i] for i in indices]
        values = [c.value for c in cards]
        if len(set(values)) != 1:
            return False , "all card must have the same value"

        if not isValidCard(self.current_pile, cards[0]):
            return False, "Invalid move."

        for i in sorted(indices, reverse=True):
            player.remove_card_from_hand_by_index(i)

        for card in cards:
            self.current_pile.append(card)

        burned = False
        if self.check_if_burn():
            self.burn_pile()
            burned = True

        self.refill_hand(player)
        self.remove_finished_players()

        if self.state == "game_over":
            return True, f"{player.name} played {len(cards)} cards of {cards[0]} Game over."

        if burned:
            return True, f"{player.name} played {len(cards)} cards of {cards[0]} Pile burned! Play again."

        steps = 1
        if checkValue(cards[0]) == 6:
            steps = 2
        self.advance_turn(steps)
        return True, f"{player.name} played {len(cards)} cards of {cards[0]}."



    def play_face_up_card(self, player, indices):
        for i in indices:
            if i < 0 or i >= len(player.face_up):
                return False, "Invalid card index."

        cards = [player.face_up[i] for i in indices]
        values = [c.value for c in cards]
        if len(set(values)) != 1:
            return False, "all card must have the same value"

        if not isValidCard(self.current_pile, cards[0]):
            return False, "Invalid move."

        for i in sorted(indices, reverse=True):
            player.face_up.pop(i)

        for card in cards:
            self.current_pile.append(card)

        burned = False
        if self.check_if_burn():
            self.burn_pile()
            burned = True

        self.remove_finished_players()

        if self.state == "game_over":
            return True, f"{player.name} played {cards[0]}. Game over."

        if burned:
            return True, f"{player.name} played {cards[0]}. Pile burned! Play again."

        steps = 1
        if checkValue(cards[0]) == 6:
            steps = 2
        self.advance_turn(steps)
        return True, f"{player.name} played {cards[0]}."


    def play_face_down_card(self, player, index):
        if index < 0 or index >= len(player.face_down):
            return False, "Invalid card index."

        played_card = player.face_down.pop(index)

        if isValidCard(self.current_pile, played_card):
            self.current_pile.append(played_card)

            burned = False
            if self.check_if_burn():
                self.burn_pile()
                burned = True

            self.remove_finished_players()

            if self.state == "game_over":
                return True, f"{player.name} revealed {played_card}. Game over."

            if burned:
                return True, f"{player.name} revealed {played_card}. Pile burned! Play again."

            steps = 1
            if checkValue(played_card) == 6:
                steps = 2
            self.advance_turn(steps)
            return True, f"{player.name} revealed {played_card} and played it."

        # לא חוקי -> לוקח pile וגם את הקלף ההפוך
        player.take_card(played_card)
        self.pickup_pile(player)
        self.advance_turn()
        return True, f"{player.name} revealed {played_card}. Bad luck, picked up the pile."




    def take_pile_by_choice(self):
        player = self.get_current_player()
        if player is None:
            return False, "No current player."
        if len(self.current_pile) == 0:
            return False, "Pile is empty."
        self.pickup_pile(player)
        self.advance_turn()
        return True, f"{player.name} took the pile."















