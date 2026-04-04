from network import Network


def main():
    # 1. השליח מתחבר לשרת
    n = Network()

    # מבררים איזה שחקן אנחנו (0 או 1)
    player_id = n.getP()
    print(f"Connected! I am Player number {player_id}")

    while True:
        input("\nPress Enter to ask the server for the game state...")

        # 2. שולחים לשרת בקשה לקבל את אובייקט ה-Game
        game = n.send("get")

        # מוודאים שאכן קיבלנו משחק ושני השחקנים כבר מחוברים
        if len(game.Players) == 2:
            # שולפים את השחקן שלנו מתוך המשחק שקיבלנו מהשרת!
            my_player = game.Players[player_id]

            print(f"--- My Cards (Player {player_id}) ---")
            # מדפיסים את הקלפים שלנו כדי להוכיח שזה עובד
            print(f"Hand: {[str(c) for c in my_player.hand]}")
            print(f"Face Up: {[str(c) for c in my_player.face_up]}")
            print(f"Face Down: {len(my_player.face_down)} cards")
            print("-" * 35)
        else:
            print("Waiting for Player 1 to connect so the server can deal cards...")


if __name__ == "__main__":
    main()