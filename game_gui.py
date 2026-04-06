import pygame
from network import Network


class ShitheadGUI:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1300
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("arial", 26)

        self.running = True
        self.message = ""

        # מצבי תצוגה: MENU, WAITING, PLAYING
        self.gui_state = "MENU"
        self.target_players = 0  # כמה שחקנים המשתמש בחר

        # כפתורי תפריט
        self.btn_2p = pygame.Rect(self.WIDTH // 2 - 100, 300, 200, 60)
        self.btn_3p = pygame.Rect(self.WIDTH // 2 - 100, 400, 200, 60)
        self.btn_4p = pygame.Rect(self.WIDTH // 2 - 100, 500, 200, 60)

        # משתני משחק קיימים
        self.hand_rects = []
        self.face_up_rects = []
        self.face_down_rects = []
        self.confirm_rect = pygame.Rect(980, 60, 170, 45)
        self.play_confirm_rect = pygame.Rect(980, 120, 170, 45)
        self.pile_rect = None
        self.selected_play_indices = []
        self.selected_play_zone = None

        # חיבור לרשת
        self.network = Network()
        self.player_id = None  # נקבל מהשרת רק כשהמשחק יתחיל
        self.game = None

        pygame.display.set_caption("Shithead Online")

    def run(self):
        while self.running:
            self.handle_events()

            # לוגיקת עדכון מהשרת
            if self.gui_state == "WAITING" or self.gui_state == "PLAYING":
                # אנחנו שולחים "get" כדי לקבל עדכון
                response = self.network.send("get")
                if response:
                    if response.get("status") == "playing":
                        self.gui_state = "PLAYING"
                        self.game = response.get("game")
                        self.player_id = response.get("player_id")
                    elif response.get("status") == "waiting":
                        self.message = response.get("message", "Waiting...")

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.gui_state == "MENU":
                    self.handle_menu_click(event.pos)
                elif self.gui_state == "PLAYING":
                    self.handle_mouse_click(event.pos)

    def handle_mouse_click(self, pos):
        if not self.game or len(self.game.Players) < 2:
            return

        # בדיקה האם זה התור שלי בכלל
        my_turn_setup = (self.game.state == "setup" and self.game.setup_player_index == self.player_id)
        my_turn_play = (self.game.state == "playing" and self.game.current_player == self.player_id)

        if self.game.state == "setup" and self.confirm_rect.collidepoint(pos):
            if my_turn_setup:
                self.network.send({"action": "setup_confirm"})
            else:
                self.message = "Not your turn!"
            return

        if self.game.state == "playing" and self.selected_play_indices and self.play_confirm_rect.collidepoint(pos):
            if my_turn_play:
                self.network.send(
                    {"action": "play_cards", "zone": self.selected_play_zone, "indices": self.selected_play_indices})
                self.selected_play_indices.clear()
                self.selected_play_zone = None
            else:
                self.message = "Not your turn!"
            return

        if self.game.state == "playing" and self.pile_rect and self.pile_rect.collidepoint(pos):
            if my_turn_play:
                self.network.send({"action": "take_pile"})
            return

        for rect, index, card in self.hand_rects:
            if rect.collidepoint(pos):
                if self.game.state == "setup":
                    if my_turn_setup:
                        self.network.send({"action": "setup_toggle", "index": index})
                elif self.game.state == "playing":
                    if my_turn_play:
                        self.toggle_card_selection("hand", index, card)
                return

        for rect, index, card in self.face_up_rects:
            if rect.collidepoint(pos):
                if self.game.state == "playing" and my_turn_play:
                    self.toggle_card_selection("face_up", index, card)
                return

        for rect, index in self.face_down_rects:
            if rect.collidepoint(pos):
                if self.game.state == "playing" and my_turn_play:
                    self.network.send({"action": "play_face_down", "index": index})
                return

    def toggle_card_selection(self, zone, index, card):
        # אם בחרנו קלף מאזור אחר (למשל עברנו מהיד ל-Face Up), נאפס את הבחירה
        if self.selected_play_zone != zone:
            self.selected_play_zone = zone
            self.selected_play_indices.clear()

        # אם הקלף כבר מסומן - נבטל את הסימון שלו
        if index in self.selected_play_indices:
            self.selected_play_indices.remove(index)
            if not self.selected_play_indices:
                self.selected_play_zone = None
        else:
            # אפשר לבחור רק קלפים מאותו ערך ביחד
            if len(self.selected_play_indices) > 0:
                first_idx = self.selected_play_indices[0]
                player = self.game.Players[self.player_id]
                first_card = player.hand[first_idx] if zone == "hand" else player.face_up[first_idx]

                # מוסיפים רק אם זה אותו מספר כמו הקלף הראשון שבחרנו
                if card.value == first_card.value:
                    self.selected_play_indices.append(index)
            else:
                self.selected_play_indices.append(index)




    def handle_menu_click(self, pos):
        selection = None
        if self.btn_2p.collidepoint(pos):
            selection = 2
        elif self.btn_3p.collidepoint(pos):
            selection = 3
        elif self.btn_4p.collidepoint(pos):
            selection = 4

        if selection:
            self.target_players = selection
            # שליחת בקשת הצטרפות לשרת
            response = self.network.join_queue(selection)
            if response:
                self.gui_state = "WAITING"
                self.message = response.get("message", "Searching for match...")

    def draw(self):
        self.screen.fill((20, 120, 20))  # רקע ירוק

        if self.gui_state == "MENU":
            self.draw_menu()
        elif self.gui_state == "WAITING":
            self.draw_waiting()
        elif self.gui_state == "PLAYING":
            self.draw_game_screen()

    def draw_menu(self):
        title = self.font.render("SHITHEAD ONLINE", True, (255, 255, 255))
        self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 150))

        instruction = self.small_font.render("Select number of players:", True, (200, 200, 200))
        self.screen.blit(instruction, (self.WIDTH // 2 - instruction.get_width() // 2, 240))

        for btn, txt in [(self.btn_2p, "2 Players"), (self.btn_3p, "3 Players"), (self.btn_4p, "4 Players")]:
            pygame.draw.rect(self.screen, (255, 255, 255), btn, border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), btn, 2, border_radius=10)
            text = self.small_font.render(txt, True, (0, 0, 0))
            self.screen.blit(text, (btn.x + (btn.width - text.get_width()) // 2, btn.y + 15))

    def draw_waiting(self):
        # מסך טעינה פשוט
        title = self.font.render("Looking for Players...", True, (255, 255, 255))
        self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 300))

        msg = self.small_font.render(self.message, True, (255, 255, 0))
        self.screen.blit(msg, (self.WIDTH // 2 - msg.get_width() // 2, 400))

    def draw_game_screen(self):
        # כאן נכנסת כל פונקציית ה-draw המקורית שלך!
        # (draw_title, draw_pile, draw_current_player_cards וכו')
        # שים לב להשתמש ב-self.player_id שקיבלנו מהשרת
        if not self.game: return

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
                prefix = "*** YOUR TURN *** " if self.game.setup_player_index == self.player_id else ""
                text = f"{prefix}Setup: {player.name}, choose 3 cards for face up"
        elif self.game.state == "playing":
            player = self.game.get_current_player()
            if player:
                prefix = "*** YOUR TURN *** " if self.game.current_player == self.player_id else ""
                text = f"{prefix}Turn: {player.name}"
        else:
            text = "Game Over"

        state_text = self.small_font.render(text, True, (255, 255, 255))
        self.screen.blit(state_text, (20, 95))

    def draw_confirm_button(self):
        if self.game.state == "setup" and self.game.setup_player_index == self.player_id:
            pygame.draw.rect(self.screen, (230, 230, 230), self.confirm_rect)
            pygame.draw.rect(self.screen, (255, 0, 0), self.confirm_rect, 2)
            text = self.small_font.render("Confirm 3 Cards", True, (0, 0, 0))
            self.screen.blit(text, (self.confirm_rect.x + 15, self.confirm_rect.y + 13))

        elif self.game.state == "playing" and self.selected_play_indices and self.game.current_player == self.player_id:
            pygame.draw.rect(self.screen, (230, 230, 230), self.play_confirm_rect)
            pygame.draw.rect(self.screen, (255, 0, 0), self.play_confirm_rect, 2)
            text = self.small_font.render("Play Selected", True, (0, 0, 0))
            self.screen.blit(text, (self.play_confirm_rect.x + 20, self.play_confirm_rect.y + 13))

    def draw_pile(self):
        self.pile_rect = pygame.Rect(520, 220, 120, 150)
        pygame.draw.rect(self.screen, (255, 255, 255), self.pile_rect)
        pygame.draw.rect(self.screen, (255, 0, 0), self.pile_rect, 2)

        pile_title = self.small_font.render(f"Pile ({len(self.game.current_pile)})", True, (0, 0, 0))
        self.screen.blit(pile_title, (540, 230))

        if len(self.game.current_pile) > 0:
            top_card = str(self.game.current_pile[-1])
            card_text = self.small_font.render(top_card, True, (0, 0, 0))
            self.screen.blit(card_text, (535, 295))
        else:
            empty_text = self.small_font.render("Empty", True, (0, 0, 0))
            self.screen.blit(empty_text, (555, 295))

    def draw_current_player_cards(self):
        # הממשק מציג *תמיד* את הקלפים שלך, גם אם זה לא תורך!
        if self.player_id < len(self.game.Players):
            player = self.game.Players[self.player_id]
        else:
            return

        self.hand_rects = []
        self.face_up_rects = []
        self.face_down_rects = []

        card_width = 80
        card_height = 120
        gap = 15
        row_gap = 20
        cards_per_row = 8

        def get_row_start_x(row_count):
            total_width = row_count * card_width + (row_count - 1) * gap
            return (self.WIDTH - total_width) // 2

        hand_y = 400
        left_cards_x = 40

        cards_text = self.small_font.render("Your cards", True, (255, 255, 255))
        zone_text = self.small_font.render(f"Active zone: {player.active_cards()[1]}", True, (255, 255, 0))
        self.screen.blit(cards_text, (20, 420))
        self.screen.blit(zone_text, (20, 455))

        hand_title = self.small_font.render("Hand", True, (255, 255, 255))
        hand_title_x = self.WIDTH // 2 - hand_title.get_width() // 2
        self.screen.blit(hand_title, (hand_title_x, hand_y - 35))

        for i, card in enumerate(player.hand):
            row = i // cards_per_row
            col = i % cards_per_row
            row_count = min(cards_per_row, len(player.hand) - row * cards_per_row)
            row_start_x = get_row_start_x(row_count)
            x = row_start_x + col * (card_width + gap)
            y = hand_y + row * (card_height + row_gap)
            rect = pygame.Rect(x, y, card_width, card_height)

            is_selected = False
            if self.game.state == "setup" and i in self.game.selected_indices and self.game.setup_player_index == self.player_id:
                is_selected = True
            if self.game.state == "playing" and self.selected_play_zone == "hand" and i in self.selected_play_indices:
                is_selected = True

            pygame.draw.rect(self.screen, (255, 230, 120) if is_selected else (255, 255, 255), rect)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)

            card_color = (255, 0, 0) if card.suit in ["Hearts", "Diamonds"] else (0, 0, 0)
            card_text = self.small_font.render(str(card), True, card_color)
            self.screen.blit(card_text, (x + card_width // 2 - card_text.get_width() // 2,
                                         y + card_height // 2 - card_text.get_height() // 2))
            self.hand_rects.append((rect, i, card))

        hand_rows = max(1, (len(player.hand) + cards_per_row - 1) // cards_per_row)
        hand_bottom = hand_y + hand_rows * card_height + (hand_rows - 1) * row_gap

        face_up_y = hand_bottom + 70
        face_down_y = face_up_y + card_height + 40

        face_up_title = self.small_font.render("Face Up", True, (255, 255, 255))
        self.screen.blit(face_up_title, (left_cards_x, face_up_y - 35))

        for i, card in enumerate(player.face_up):
            x = left_cards_x + i * (card_width + gap)
            rect = pygame.Rect(x, face_up_y, card_width, card_height)
            is_selected = (
                        self.game.state == "playing" and self.selected_play_zone == "face_up" and i in self.selected_play_indices)

            pygame.draw.rect(self.screen, (255, 230, 120) if is_selected else (255, 255, 255), rect)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)

            card_color = (255, 0, 0) if card.suit in ["Hearts", "Diamonds"] else (0, 0, 0)
            card_text = self.small_font.render(str(card), True, card_color)
            self.screen.blit(card_text, (x + card_width // 2 - card_text.get_width() // 2,
                                         face_up_y + card_height // 2 - card_text.get_height() // 2))
            self.face_up_rects.append((rect, i, card))

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