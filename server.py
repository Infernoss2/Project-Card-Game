import socket
import pickle
import threading
import uuid
from Game import Game

SERVER_IP = "127.0.0.1"
PORT = 5555

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, PORT))
server_socket.listen()

print(f"Server is running on {SERVER_IP}:{PORT}")
print("Waiting for connections...")

# תורי המתנה לפי מספר שחקנים מבוקש
waiting_queues = {
    2: [],
    3: [],
    4: []
}

active_rooms = {}
# עכשיו נשמור פה מילון קטן עם ה-room_id וגם ה-player_index של כל שחקן
client_to_room = {}
queue_lock = threading.Lock()


def handle_client(conn, addr):
    print(f"New connection from {addr}")

    try:
        data = conn.recv(1024)
        if not data:
            return

        join_request = pickle.loads(data)
        target_players = join_request.get("target_players", 2)

        # שלב 2: טיפול בתור ההמתנה ויצירת חדרים
        with queue_lock:
            queue = waiting_queues[target_players]
            player_index = len(queue)
            player_name = f"Player {player_index + 1}"

            queue.append((conn, player_name))
            print(f"[{addr}] joined queue for {target_players} players. Queue status: {len(queue)}/{target_players}")

            if len(queue) == target_players:
                room_id = str(uuid.uuid4())
                new_game = Game()

                # שמירת ה-ID של החדר והאינדקס של השחקן בצורה בטוחה ויעילה
                for i, (c, p_name) in enumerate(queue):
                    new_game.add_player(p_name)
                    client_to_room[c] = {"room_id": room_id, "player_index": i}

                new_game.deal_cards()
                active_rooms[room_id] = new_game

                print(f"Room {room_id} created with {target_players} players! Game started.")
                waiting_queues[target_players].clear()

                # התיקון הקריטי: אנחנו חייבים לשלוח תשובה חזרה גם לשחקן האחרון שהשלים את החדר!
                conn.sendall(pickle.dumps({"status": "waiting", "message": "Game Starting!"}))
            else:
                conn.sendall(pickle.dumps(
                    {"status": "waiting", "message": f"Waiting for {target_players - len(queue)} more players..."}))

        # שלב 3: לולאת המשחק המרכזית
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                request = pickle.loads(data)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

            # שולפים את המידע על החדר והשחקן ישירות מהמילון המעודכן שלנו
            room_info = client_to_room.get(conn)

            if not room_info:
                conn.sendall(pickle.dumps({"status": "waiting", "message": "Waiting for more players..."}))
                continue

            room_id = room_info["room_id"]
            player_index = room_info["player_index"]
            game = active_rooms[room_id]

            # לוגיקה אוטומטית של המשחק (לקיחת קופה אם אין ברירה)
            if game.state == "playing" and len(game.current_pile) > 0:
                curr_p = game.get_current_player()
                if curr_p and not game.can_player_play_any(curr_p):
                    game.pickup_pile(curr_p)
                    game.advance_turn()

            # פיענוח פקודות מהלקוח
            if isinstance(request, dict):
                action = request.get("action")

                if action == "setup_toggle" and game.setup_player_index == player_index:
                    game.toggle_setup_card(request["index"])
                elif action == "setup_confirm" and game.setup_player_index == player_index:
                    game.confirm_setup_selection()
                elif action == "play_cards" and game.current_player == player_index:
                    game.play_selected_cards(request["zone"], request["indices"])
                elif action == "play_face_down" and game.current_player == player_index:
                    game.handle_card_click("face_down", request["index"])
                elif action == "take_pile" and game.current_player == player_index:
                    game.take_pile_by_choice()

            # שליחת מצב המשחק המעודכן חזרה ללקוח
            response = {
                "status": "playing",
                "player_id": player_index,
                "game": game
            }
            conn.sendall(pickle.dumps(response))

    except Exception as e:
        print(f"Connection error with {addr}: {e}")
    finally:
        print(f"Client {addr} disconnected.")
        conn.close()


while True:
    conn, addr = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()