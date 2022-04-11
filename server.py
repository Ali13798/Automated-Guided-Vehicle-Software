import atexit
import socket
import threading

FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
HEADERSIZE = 16


class Server:
    def __init__(self, ip: str, port: int) -> None:
        self.SERVER = ip
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((ip, port))

    def handle_client(self, client: socket.socket, addr) -> None:
        print(f"[NEW CONNECTION] {addr} connected.")

        connected = True
        while connected:
            msg_length = client.recv(HEADERSIZE).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = client.recv(msg_length).decode(FORMAT)
                print(f"[{addr}] {msg}")

                if msg == DISCONNECT_MESSAGE:
                    connected = False

        # If not connected close the socket
        client.close()

    def start(self):
        self.server.listen()
        print(f"[LISTENNING] Server is listenning on {self.SERVER}")
        client, addr = self.server.accept()
        thread = threading.Thread(
            target=self.handle_client, args=(client, addr)
        )
        thread.start()
        # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def main():
    PORT = 1234
    SERVER = socket.gethostbyname(socket.gethostname())

    server = Server(ip=SERVER, port=PORT)

    print("[STARTING] server is starting...")
    server.start()


if __name__ == "__main__":
    main()
