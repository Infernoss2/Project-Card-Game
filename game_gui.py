import pygame
from Game import Game


class ShitheadGUI:
    def __init__(self):
        pygame.init()

        self.WIDTH = 1300
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Shithead")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont("arial", 26)

        self.running = True
        self.message = "Welcome to Shithead"

        self.hand_rects = []
        self.face_up_rects = []
        self.face_down_rects = []
        self.confirm_rect = pygame.Rect(980, 60, 170, 45)

        self.selected_play_indices = []
        self.selected_play_zone = None
        self.pile_rect = None
        self.play_confirm_rect = pygame.Rect(980, 120, 170, 45)

        self.game = Game()
        self.game.add_player("sagi")
        self.game.add_player("nami")
        self.game.add_player("zoro")

        self.game.deal_cards()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def toggle_card_selection(self, zone, index, card):
        current_player = self.game.get_current_player()
        if current_player is None:
            return

        active_cards, active_zone = current_player.active_cards()
        if zone != active_zone:
            self.message = "You can only select from the active zone."
            return

        if self.selected_play_zone is None:
            self.selected_play_zone = zone

        if zone != self.selected_play_zone:
            self.message = "You can only select cards from one zone."
            return

        if index in self.selected_play_indices:
            self.selected_play_indices.remove(index)
            if not self.selected_play_indices:
                self.selected_play_zone = None
            return

        selected_cards = []
        if zone == "hand":
            selected_cards = [current_player.hand[i] for i in self.selected_play_indices]
        elif zone == "face_up":
            selected_cards = [current_player.face_up[i] for i in self.selected_play_indices]

        if selected_cards and card.value != selected_cards[0].value:
            self.message = "You can only select cards with the same value."
            return

        self.selected_play_indices.append(index)
        self.selected_play_indices.sort()

    def handle_mouse_click(self, pos):
        if self.game.state == "setup" and self.confirm_rect.collidepoint(pos):
            success, message = self.game.confirm_setup_selection()
            self.message = message
            return

        if self.game.state == "playing" and self.selected_play_indices and self.play_confirm_rect.collidepoint(pos):
            success, message = self.game.play_selected_cards(self.selected_play_zone, self.selected_play_indices)
            self.message = message
            self.selected_play_indices.clear()
            self.selected_play_zone = None
            return

        if self.game.state == "playing" and self.pile_rect and self.pile_rect.collidepoint(pos):
            success, message = self.game.take_pile_by_choice()
            self.message = message
            self.selected_play_indices.clear()
            self.selected_play_zone = None
            return


        # hand
        for rect, index, card in self.hand_rects:
            if rect.collidepoint(pos):
                if self.game.state == "setup":
                    success, message = self.game.toggle_setup_card(index)
                    self.message = message
                    return

                if self.game.state == "playing":
                    self.toggle_card_selection("hand", index, card)
                    return

        # face up
        for rect, index, card in self.face_up_rects:
            if rect.collidepoint(pos):
                if self.game.state == "playing":
                    self.toggle_card_selection("face_up", index, card)
                    return

        # face down
        for rect, index in self.face_down_rects:
            if rect.collidepoint(pos):
                success, message = self.game.handle_card_click("face_down", index)
                self.message = message
                return




    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)

    def draw(self):
        self.screen.fill((20, 120, 20))

        self.draw_title()
        self.draw_message()
        self.draw_state()
        self.draw_pile()
        self.draw_confirm_button()
        self.draw_current_player_cards()
        self.draw_results_table()

    def draw_title(self):
        title = self.font.render("Shithead", True, (255, 255, 255))
        self.screen.blit(title, (20, 20))

    def draw_message(self):
        text = self.small_font.render(self.message, True, (255, 255, 0))
        self.screen.blit(text, (20, 60))

    def draw_state(self):
        if self.game.state == "setup":
            player = self.game.get_setup_player()
            if player:
                text = f"Setup: {player.name}, choose 3 cards for face up"
            else:
                text = "Setup"
        elif self.game.state == "playing":
            player = self.game.get_current_player()
            if player:
                text = f"Turn: {player.name}"
            else:
                text = "Playing"
        else:
            text = "Game Over"

        state_text = self.small_font.render(text, True, (255, 255, 255))
        self.screen.blit(state_text, (20, 95))

    def draw_confirm_button(self):
        if self.game.state == "setup":
            pygame.draw.rect(self.screen, (230, 230, 230), self.confirm_rect)
            pygame.draw.rect(self.screen, (255, 0, 0), self.confirm_rect, 2)
            text = self.small_font.render("Confirm 3 Cards", True, (0, 0, 0))
            self.screen.blit(text, (self.confirm_rect.x + 15, self.confirm_rect.y + 13))

        elif self.game.state == "playing" and self.selected_play_indices:
            pygame.draw.rect(self.screen, (230, 230, 230), self.play_confirm_rect)
            pygame.draw.rect(self.screen, (255, 0, 0), self.play_confirm_rect, 2)
            text = self.small_font.render("Play Selected", True, (0, 0, 0))
            self.screen.blit(text, (self.play_confirm_rect.x + 20, self.play_confirm_rect.y + 13))

    def draw_pile(self):
        self.pile_rect = pygame.Rect(520, 220, 120, 150)
        pygame.draw.rect(self.screen, (255, 255, 255), self.pile_rect)
        pygame.draw.rect(self.screen, (255, 0, 0), self.pile_rect, 2)

        pile_title = self.small_font.render("Pile", True, (0, 0, 0))
        self.screen.blit(pile_title, (560, 230))

        if len(self.game.current_pile) > 0:
            top_card = str(self.game.current_pile[-1])
            card_text = self.small_font.render(top_card, True, (0, 0, 0))
            self.screen.blit(card_text, (535, 295))
        else:
            empty_text = self.small_font.render("Empty", True, (0, 0, 0))
            self.screen.blit(empty_text, (555, 295))

    def draw_current_player_cards(self):
        if self.game.state == "setup":
            player = self.game.Players[self.game.setup_player_index]
        else:
            player = self.game.get_current_player()

        if player is None:
            return

        self.hand_rects = []
        self.face_up_rects = []
        self.face_down_rects = []

        card_width = 80
        card_height = 120
        gap = 15
        row_gap = 20
        cards_per_row = 8

        # ---------- helper ----------
        def get_row_start_x(row_count):
            total_width = row_count * card_width + (row_count - 1) * gap
            return (self.WIDTH - total_width) // 2

        # ---------- base positions ----------
        hand_y = 400
        left_cards_x = 40

        # ---------- player info ----------
        cards_text = self.small_font.render(f"{player.name}'s cards", True, (255, 255, 255))
        zone_text = self.small_font.render(f"Active zone: {player.active_cards()[1]}", True, (255, 255, 0))
        self.screen.blit(cards_text, (20, 420))
        self.screen.blit(zone_text, (20, 455))

        # ---------- Hand title ----------
        hand_title = self.small_font.render("Hand", True, (255, 255, 255))
        hand_title_x = self.WIDTH // 2 - hand_title.get_width() // 2
        self.screen.blit(hand_title, (hand_title_x, hand_y - 35))

        # ---------- Hand cards ----------
        for i, card in enumerate(player.hand):
            row = i // cards_per_row
            col = i % cards_per_row

            row_count = min(cards_per_row, len(player.hand) - row * cards_per_row)
            row_start_x = get_row_start_x(row_count)

            x = row_start_x + col * (card_width + gap)
            y = hand_y + row * (card_height + row_gap)

            rect = pygame.Rect(x, y, card_width, card_height)

            is_selected = False
            if self.game.state == "setup" and i in self.game.selected_indices:
                is_selected = True
            if self.game.state == "playing" and self.selected_play_zone == "hand" and i in self.selected_play_indices:
                is_selected = True

            if is_selected:
                pygame.draw.rect(self.screen, (255, 230, 120), rect)
            else:
                pygame.draw.rect(self.screen, (255, 255, 255), rect)

            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)

            card_color = (255, 0, 0) if card.suit in ["Hearts", "Diamonds"] else (0, 0, 0)
            card_text = self.small_font.render(str(card), True, card_color)
            text_x = x + card_width // 2 - card_text.get_width() // 2
            text_y = y + card_height // 2 - card_text.get_height() // 2
            self.screen.blit(card_text, (text_x, text_y))

            self.hand_rects.append((rect, i, card))

        # ---------- calculate dynamic positions ----------
        hand_rows = max(1, (len(player.hand) + cards_per_row - 1) // cards_per_row)
        hand_bottom = hand_y + hand_rows * card_height + (hand_rows - 1) * row_gap

        face_up_y = hand_bottom + 70
        face_down_y = face_up_y + card_height + 40

        # ---------- Face Up ----------
        face_up_title = self.small_font.render("Face Up", True, (255, 255, 255))
        self.screen.blit(face_up_title, (left_cards_x, face_up_y - 35))

        for i, card in enumerate(player.face_up):
            x = left_cards_x + i * (card_width + gap)
            rect = pygame.Rect(x, face_up_y, card_width, card_height)

            is_selected = (
                    self.game.state == "playing"
                    and self.selected_play_zone == "face_up"
                    and i in self.selected_play_indices
            )

            if is_selected:
                pygame.draw.rect(self.screen, (255, 230, 120), rect)
            else:
                pygame.draw.rect(self.screen, (255, 255, 255), rect)

            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)

            card_color = (255, 0, 0) if card.suit in ["Hearts", "Diamonds"] else (0, 0, 0)
            card_text = self.small_font.render(str(card), True, card_color)
            text_x = x + card_width // 2 - card_text.get_width() // 2
            text_y = face_up_y + card_height // 2 - card_text.get_height() // 2
            self.screen.blit(card_text, (text_x, text_y))

            self.face_up_rects.append((rect, i, card))

        # ---------- Face Down ----------
        face_down_title = self.small_font.render("Face Down", True, (255, 255, 255))
        self.screen.blit(face_down_title, (left_cards_x, face_down_y - 35))

        for i, card in enumerate(player.face_down):
            x = left_cards_x + i * (card_width + gap)
            rect = pygame.Rect(x, face_down_y, card_width, card_height)

            pygame.draw.rect(self.screen, (60, 60, 180), rect)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)

            self.face_down_rects.append((rect, i))

    def draw_results_table(self):
        if self.game.state != "game_over":
            return

        title = self.font.render("Final Standings", True, (255, 255, 255))
        self.screen.blit(title, (850, 220))

        for i, name in enumerate(self.game.finish_order):
            text = self.small_font.render(f"{i + 1}. {name}", True, (255, 255, 255))
            self.screen.blit(text, (850, 270 + i * 35))


if __name__ == "__main__":
    gui = ShitheadGUI()
    gui.run()