import socket
import pickle

SERVER_IP = "127.0.0.1"
PORT = 5555

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))

# מקבלים את המידע מהשרת
raw_data = client_socket.recv(4096)

# מרכיבים חזרה את האובייקט בעזרת פיקל
received_game_state = pickle.loads(raw_data)

# עכשיו זה שוב מילון אמיתי של פייתון! אפשר לגשת לערכים שלו:
print("--- Received Data from Server ---")
print(f"Full Dictionary: {received_game_state}")
print(f"Whose turn is it? -> {received_game_state['current_turn']}")

client_socket.close()