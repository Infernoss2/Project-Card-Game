import socket
import pickle
import threading
from Game import Game

SERVER_IP = "127.0.0.1"
PORT = 5555

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, PORT))
server_socket.listen()

print(f"Server is running on {SERVER_IP}:{PORT}")
print("Waiting for connections...")

game = Game()
players_connected = 0


def handle_client(conn, player_index):
    global players_connected

    # שליחת מספר השחקן ללקוח החדש
    conn.send(str.encode(str(player_index)))

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            request = pickle.loads(data)

            # בדיקה אוטומטית: האם השחקן שכרגע תורו חייב לקחת את הקופה?
            if game.state == "playing" and len(game.current_pile) > 0:
                curr_p = game.get_current_player()
                if curr_p and not game.can_player_play_any(curr_p):
                    game.pickup_pile(curr_p)
                    game.advance_turn()

            # פיענוח הפקודות שמגיעות מה-GUI
            if isinstance(request, dict):
                action = request.get("action")

                # פעולות Setup
                if action == "setup_toggle" and game.setup_player_index == player_index:
                    game.toggle_setup_card(request["index"])
                elif action == "setup_confirm" and game.setup_player_index == player_index:
                    game.confirm_setup_selection()

                # פעולות משחק רגיל
                elif action == "play_cards" and game.current_player == player_index:
                    game.play_selected_cards(request["zone"], request["indices"])
                elif action == "play_face_down" and game.current_player == player_index:
                    game.handle_card_click("face_down", request["index"])
                elif action == "take_pile" and game.current_player == player_index:
                    game.take_pile_by_choice()

            # השרת תמיד מחזיר ללקוח את המשחק המעודכן
            conn.sendall(pickle.dumps(game))

        except Exception as e:
            print(f"Error with Player {player_index}: {e}")
            break

    print(f"Player {player_index} disconnected.")
    players_connected -= 1
    conn.close()


while True:
    conn, addr = server_socket.accept()
    print(f"Connected to: {addr}")

    player_name = f"Player {players_connected + 1}"
    game.add_player(player_name)

    players_connected += 1
    if players_connected == 2:
        print("2 Players connected! Dealing cards...")
        game.deal_cards()

    thread = threading.Thread(target=handle_client, args=(conn, players_connected - 1))
    thread.start()