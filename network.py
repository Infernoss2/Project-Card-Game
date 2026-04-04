import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect() # שמירת מספר השחקן שלנו (0, 1, 2...)

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            # השרת שולח לנו את המספר שלנו בתור טקסט רגיל בהתחלה
            return int(self.client.recv(2048).decode())
        except socket.error as e:
            print(f"Network error: {e}")

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            response = self.client.recv(8192) # הגדלנו קצת את הבאפר כדי שהמשחק הענק ייכנס בו
            return pickle.loads(response)
        except socket.error as e:
            print(f"Failed to send/receive data: {e}")
            return None