import pygame
from Game import Game


class ShitheadGUI:
    def __init__(self):
        pygame.init()
        self.hand_rects = []

        self.WIDTH = 1200
        self.HEIGHT = 700
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Shithead")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)

        self.running = True
        self.message = "Welcome to Shithead"

        # הלוגיקה של המשחק
        self.game = Game()
        self.game.add_player("You")
        self.game.add_player("CPU")
        self.game.deal_cards()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def handle_mouse_click(self , pos):
        for rect , index , card in self.hand_rects:
            if rect.collidepoint(pos):
                player = self.game.Players[self.game.current_player]
                success , message = self.game.try_play_hand_card(player , index)
                self.message = message
                return 


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)

    def draw(self):
        self.screen.fill((20, 120, 20))  # רקע ירוק

        self.draw_title()
        self.draw_message()
        self.draw_pile()
        self.draw_current_player_cards()

    def draw_title(self):
        title = self.font.render("Shithead", True, (255, 255, 255))
        self.screen.blit(title, (20, 20))

    def draw_message(self):
        text = self.small_font.render(self.message, True, (255, 255, 0))
        self.screen.blit(text, (20, 60))

    def draw_pile(self):
        # מלבן שמייצג את ה-pile
        pile_rect = pygame.Rect(450, 250, 100, 140)
        pygame.draw.rect(self.screen, (255, 255, 255), pile_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), pile_rect, 2)

        pile_title = self.small_font.render("Pile", True, (0, 0, 0))
        self.screen.blit(pile_title, (480, 260))

        # נציג את הקלף העליון אם יש
        if hasattr(self.game, "pile") and len(self.game.current_pile) > 0:
            top_card = str(self.game.current_pile[-1])
            card_text = self.small_font.render(top_card, True, (0, 0, 0))
            self.screen.blit(card_text, (470, 320))
        else:
            empty_text = self.small_font.render("Empty", True, (0, 0, 0))
            self.screen.blit(empty_text, (470, 320))

    def draw_current_player_cards(self):
        player = self.game.Players[self.game.current_player]

        title = self.font.render(f"{player.name}'s cards", True, (255, 255, 255))
        self.screen.blit(title, (20, 440))

        # active zone text
        _, zone = player.active_cards()
        zone_text = self.small_font.render(f"Active zone: {zone}", True, (255, 255, 0))
        self.screen.blit(zone_text, (20, 475))

        # face down
        fd_title = self.small_font.render("Face Down", True, (255, 255, 255))
        self.screen.blit(fd_title, (20, 500))

        for i, card in enumerate(player.face_down):
            x = 20 + i * 90
            y = 530
            rect = pygame.Rect(x, y, 80, 120)
            pygame.draw.rect(self.screen, (50, 50, 160), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

        # face up
        fu_title = self.small_font.render("Face Up", True, (255, 255, 255))
        self.screen.blit(fu_title, (320, 500))

        for i, card in enumerate(player.face_up):
            x = 320 + i * 90
            y = 530
            rect = pygame.Rect(x, y, 80, 120)
            pygame.draw.rect(self.screen, (255, 255, 255), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

            card_text = self.small_font.render(str(card), True, (0, 0, 0))
            self.screen.blit(card_text, (x + 8, y + 45))

        # hand
        hand_title = self.small_font.render("Hand", True, (255, 255, 255))
        self.screen.blit(hand_title, (620, 500))
        self.hand_rects = []
        for i, card in enumerate(player.hand):
            x = 620 + i * 90
            y = 530

            rect = pygame.Rect(x, y, 80, 120)
            self.hand_rects.append( (rect, i, card) )
            pygame.draw.rect(self.screen, (255, 255, 255), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

            card_text = self.small_font.render(str(card), True, (0, 0, 0))
            self.screen.blit(card_text, (x + 8, y + 45))



if __name__ == "__main__":
    gui = ShitheadGUI()
    gui.run()