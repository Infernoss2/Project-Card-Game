from Cards import Deck, isValidCard, checkValue
from Player import Player


class Game:
    def __init__(self):
        self.current_deck = Deck()
        self.Players = []
        self.current_pile = []
        self.current_player = 0
        self.trash = []

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

                self.Players.pop(i)
            else:
                i += 1

        if len(self.Players) <= 1:
            self.state = "game_over"
            self.current_player = 0
            return

        if removed_current:
            self.current_player %= len(self.Players)

    def advance_turn(self):
        self.remove_finished_players()

        if self.state == "game_over":
            return

        self.current_player = (self.current_player + 1) % len(self.Players)

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
            # בזמן setup מותר לבחור רק מהיד של שחקן ה-setup
            if zone != "hand":
                return False, "Choose cards from your hand."

            return self.toggle_setup_card(index)

        if self.state == "playing":
            player = self.get_current_player()
            if player is None:
                return False, "No current player."

            cards, active_zone = player.active_cards()
            if active_zone is None:
                return False, "No cards left."

            # מותר ללחוץ רק על האזור הפעיל
            if zone != active_zone:
                return False, f"You must play from {active_zone}."

            if zone == "hand":
                return self.play_hand_card(player, index)

            if zone == "face_up":
                return self.play_face_up_card(player, index)

            if zone == "face_down":
                return self.play_face_down_card(player, index)

            return False, "Unknown zone."

        if self.state == "game_over":
            return False, "Game over."

        return False, "Unknown state."

    # -----------------------------
    # מהלכים לפי אזור
    # -----------------------------
    def play_hand_card(self, player, index):
        if index < 0 or index >= len(player.hand):
            return False, "Invalid card index."

        has_valid_card = False
        for c in player.hand:
            if isValidCard(self.current_pile, c):
                has_valid_card = True
                break

        if not has_valid_card:
            for c in self.current_pile:
                player.take_card(c)
            self.current_pile.clear()
            self.advance_turn()
            return True, f"{player.name} has no valid move and picked up the pile."

        card = player.hand[index]

        if not isValidCard(self.current_pile, card):
            return False, "Invalid move."

        played_card = player.remove_card_from_hand_by_index(index)
        self.current_pile.append(played_card)

        burned = False
        if self.check_if_burn():
            self.burn_pile()
            burned = True

        self.refill_hand(player)
        self.remove_finished_players()

        if self.state == "game_over":
            return True, f"{player.name} played {played_card}. Game over."

        if burned:
            return True, f"{player.name} played {played_card}. Pile burned! Play again."

        self.advance_turn()
        return True, f"{player.name} played {played_card}."

    def play_face_up_card(self, player, index):
        if index < 0 or index >= len(player.face_up):
            return False, "Invalid card index."

        card = player.face_up[index]

        if not isValidCard(self.current_pile, card):
            return False, "Invalid move."

        played_card = player.face_up.pop(index)
        self.current_pile.append(played_card)

        burned = False
        if self.check_if_burn():
            self.burn_pile()
            burned = True

        self.remove_finished_players()

        if self.state == "game_over":
            return True, f"{player.name} played {played_card}. Game over."

        if burned:
            return True, f"{player.name} played {played_card}. Pile burned! Play again."

        self.advance_turn()
        return True, f"{player.name} played {played_card}."

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

            self.advance_turn()
            return True, f"{player.name} revealed {played_card} and played it."

        # לא חוקי -> לוקח pile וגם את הקלף ההפוך
        player.take_card(played_card)
        self.pickup_pile(player)
        self.advance_turn()
        return True, f"{player.name} revealed {played_card}. Bad luck, picked up the pile."

    # -----------------------------
    # פעולה יזומה: לקחת pile
    # -----------------------------
    def take_pile_for_current_player(self):
        if self.state != "playing":
            return False, "You can't take the pile now."

        player = self.get_current_player()
        if player is None:
            return False, "No current player."

        if len(self.current_pile) == 0:
            return False, "Pile is empty."

        self.pickup_pile(player)
        self.advance_turn()
        return True, f"{player.name} took the pile."














