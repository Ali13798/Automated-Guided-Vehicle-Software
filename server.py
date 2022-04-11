import socket
import threading

from config import read_config

conf = read_config()
FORMAT = conf.socket_encoding_format
HEADERSIZE = conf.socket_message_header_size
DISCONNECT_MESSAGE = conf.socket_disconnect_message
HANDSHAKE = conf.socket_establish_connection_message


class Server:
    def __init__(self, ip: str, port: int) -> None:
        self.SERVER = ip
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((ip, port))

    def start(self):
        self.server.listen()
        print(f"[LISTENNING] Server is listenning on {self.SERVER}")

        self.client, addr = self.server.accept()

        self.connected = self.establish_connection()

        thread = threading.Thread(target=self.handle_client, args=(addr,))
        thread.start()

    def send_message(self, msg: str) -> None:
        message = msg.encode(FORMAT)

        msg_length = len(message)
        send_length = f"{msg_length:<{HEADERSIZE}}"

        self.client.send(send_length.encode(FORMAT))
        self.client.send(message)

        print(f"[SENDING] length {msg_length:>3}: {msg}")

    def read_message(self) -> str | None:
        msg_length = self.client.recv(HEADERSIZE).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = self.client.recv(msg_length).decode(FORMAT)
            return msg

    def establish_connection(self):
        self.send_message(HANDSHAKE)
        msg = self.read_message()

        if msg == HANDSHAKE:
            return True
        print("[CONN ERROR] Client connection failed.")
        return False

    def handle_client(self, addr: str) -> None:
        print(f"[NEW CONNECTION] {addr} connected.")

        # connected = True
        while self.connected:
            msg = self.read_message()
            if msg is None:
                continue

            print(f"[{addr}] {msg}")

            if msg == DISCONNECT_MESSAGE:
                self.connected = False

        # If not connected close the socket
        print("[Terminate] closing connection...")
        self.client.close()


def main():
    PORT = 1234
    SERVER = socket.gethostbyname(socket.gethostname())

    server = Server(ip=SERVER, port=PORT)

    print("[STARTING] server is starting...")
    server.start()


if __name__ == "__main__":
    main()
