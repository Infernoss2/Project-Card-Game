import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player_id = None  # שינוי: עכשיו לא נקבל אותו אוטומטית בהתחלה
        self.connected = self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            return True
        except socket.error as e:
            print(f"Network error: {e}")
            return False

    def join_queue(self, target_players):
        """
        שולח לשרת בקשה להיכנס לתור חיפוש משחק.
        """
        try:
            request = {"target_players": target_players}
            self.client.send(pickle.dumps(request))

            # מקבלים את התשובה הראשונית מהשרת (יכול להיות "waiting" או "playing")
            response_data = self.client.recv(8192)
            if not response_data:
                return None
            return pickle.loads(response_data)
        except socket.error as e:
            print(f"Join queue error: {e}")
            return None

    def send(self, data):
        """
        שולח פעולות רגילות לשרת תוך כדי המשחק, או מבקש את המצב הנוכחי ("get").
        """
        try:
            self.client.send(pickle.dumps(data))
            response = self.client.recv(16384)  # הגדלתי קצת את הבאפר ליתר ביטחון
            if not response:
                return None
            return pickle.loads(response)
        except socket.error as e:
            print(f"Failed to send/receive data: {e}")
            return None