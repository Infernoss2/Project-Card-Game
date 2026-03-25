import pygame
from Game import Game


class ShitheadGUI:
    def __init__(self):
        pygame.init()

        self.WIDTH = 1200
        self.HEIGHT = 700
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Shithead")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)

        self.running = True
        self.message = "Welcome to Shithead"

        self.hand_rects = []
        self.face_up_rects = []
        self.face_down_rects = []
        self.confirm_rect = pygame.Rect(980, 60, 170, 45)

        self.game = Game()
        self.game.add_player("sagi")
        self.game.add_player("bot")
        self.game.add_player("zoro")
        self.game.deal_cards()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def handle_mouse_click(self, pos):
        # כפתור confirm
        if self.game.state == "setup" and self.confirm_rect.collidepoint(pos):
            success, message = self.game.confirm_setup_selection()
            self.message = message
            return

        # hand
        for rect, index, card in self.hand_rects:
            if rect.collidepoint(pos):
                success, message = self.game.handle_card_click("hand", index)
                self.message = message
                return

        # face up
        for rect, index, card in self.face_up_rects:
            if rect.collidepoint(pos):
                success, message = self.game.handle_card_click("face_up", index)
                self.message = message
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
        if self.game.state != "setup":
            return

        pygame.draw.rect(self.screen, (230, 230, 230), self.confirm_rect)
        pygame.draw.rect(self.screen, (255, 0, 0), self.confirm_rect, 2)

        text = self.small_font.render("Confirm 3 Cards", True, (0, 0, 0))
        self.screen.blit(text, (self.confirm_rect.x + 15, self.confirm_rect.y + 13))

    def draw_pile(self):
        pile_rect = pygame.Rect(520, 220, 120, 150)
        pygame.draw.rect(self.screen, (255, 255, 255), pile_rect)
        pygame.draw.rect(self.screen, (255, 0, 0), pile_rect, 2)

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
            player = self.game.get_setup_player()
            zone_text_value = "setup"
        else:
            player = self.game.get_current_player()
            _, zone_text_value = player.active_cards() if player else (None, None)

        if player is None:
            return

        title = self.font.render(f"{player.name}'s cards", True, (255, 255, 255))
        self.screen.blit(title, (20, 420))

        zone_text = self.small_font.render(f"Active zone: {zone_text_value}", True, (255, 255, 0))
        self.screen.blit(zone_text, (20, 455))

        self.hand_rects = []
        self.face_up_rects = []
        self.face_down_rects = []

        card_width = 80
        card_height = 120
        gap = 15

        hand_y = 380
        face_up_y = 510
        face_down_y = 640

        def get_start_x(num_cards):
            if num_cards == 0:
                return self.WIDTH // 2
            total_width = num_cards * card_width + (num_cards - 1) * gap
            return (self.WIDTH - total_width) // 2

        # ---------- Hand ----------
        hand_title = self.small_font.render("Hand", True, (255, 255, 255))
        hand_title_x = self.WIDTH // 2 - hand_title.get_width() // 2
        self.screen.blit(hand_title, (hand_title_x, hand_y - 28))

        start_x = get_start_x(len(player.hand))
        for i, card in enumerate(player.hand):
            x = start_x + i * (card_width + gap)
            rect = pygame.Rect(x, hand_y, card_width, card_height)

            self.hand_rects.append((rect, i, card))

            if self.game.state == "setup" and i in self.game.selected_indices:
                pygame.draw.rect(self.screen, (255, 230, 120), rect)
            else:
                pygame.draw.rect(self.screen, (255, 255, 255), rect)

            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

            card_text = self.small_font.render(str(card), True, (255, 0, 0))
            text_x = x + (card_width - card_text.get_width()) // 2
            text_y = hand_y + card_height // 2 - card_text.get_height() // 2
            self.screen.blit(card_text, (text_x, text_y))

        # ---------- Face Up ----------
        face_up_title = self.small_font.render("Face Up", True, (255, 255, 255))
        face_up_title_x = self.WIDTH // 2 - face_up_title.get_width() // 2
        self.screen.blit(face_up_title, (face_up_title_x, face_up_y - 28))

        start_x = get_start_x(len(player.face_up))
        for i, card in enumerate(player.face_up):
            x = start_x + i * (card_width + gap)
            rect = pygame.Rect(x, face_up_y, card_width, card_height)

            self.face_up_rects.append((rect, i, card))

            pygame.draw.rect(self.screen, (255, 255, 255), rect)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)

            card_text = self.small_font.render(str(card), True, (255, 0, 0))
            text_x = x + (card_width - card_text.get_width()) // 2
            text_y = face_up_y + card_height // 2 - card_text.get_height() // 2
            self.screen.blit(card_text, (text_x, text_y))

        # ---------- Face Down ----------
        face_down_title = self.small_font.render("Face Down", True, (255, 255, 255))
        face_down_title_x = self.WIDTH // 2 - face_down_title.get_width() // 2
        self.screen.blit(face_down_title, (face_down_title_x, face_down_y - 28))

        start_x = get_start_x(len(player.face_down))
        for i, card in enumerate(player.face_down):
            x = start_x + i * (card_width + gap)
            rect = pygame.Rect(x, face_down_y, card_width, card_height)

            self.face_down_rects.append((rect, i))

            pygame.draw.rect(self.screen, (50, 50, 160), rect)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)


if __name__ == "__main__":
    gui = ShitheadGUI()
    gui.run()