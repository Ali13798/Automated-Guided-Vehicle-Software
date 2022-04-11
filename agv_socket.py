import atexit
import socket
import threading

from config import read_config


class AgvSocket:
    def __init__(self, ip: str, port: int, isServer: bool = False) -> None:

        # Configuration values
        conf = read_config()
        self.FORMAT = conf.socket_encoding_format
        self.HEADERSIZE = conf.socket_message_header_size
        self.DISCONNECT_MESSAGE = conf.socket_disconnect_message
        self.HANDSHAKE = conf.socket_establish_connection_message

        # Instance variables passed
        self.ip = ip
        self.port = port
        self.isServer = isServer

        if isServer:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((ip, port))
        else:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((ip, port))
            atexit.register(self.cleanup_server)
            self.connected = self.establish_connection()

    def establish_connection(self) -> bool:
        if self.isServer:
            self.send_message(self.HANDSHAKE)

            msg = self.read_message()
            if msg == self.HANDSHAKE:
                return True

            print("[CONN ERROR] Client connection failed.")
            return False

        # if this is not the server
        msg = self.read_message()
        if msg == self.HANDSHAKE:
            self.send_message(self.HANDSHAKE)
            print("[CONN SUCCESS] connected to the Server.")
            return True

        print("[CONN ERROR] did not connect to server.")
        return False

    def read_message(self) -> str | None:
        msg_length = self.client.recv(self.HEADERSIZE).decode(self.FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = self.client.recv(msg_length).decode(self.FORMAT)
            return msg
        return

    def send_message(self, msg: str) -> None:
        message = msg.encode(self.FORMAT)

        msg_length = len(message)
        send_length = f"{msg_length:<{self.HEADERSIZE}}"

        self.client.send(send_length.encode(self.FORMAT))
        self.client.send(message)

        print(f"[SENDING] length {msg_length:>3}: {msg}")

    def start_server(self):
        if not self.isServer:
            return

        print("[STARTING] server is starting...")

        self.server.listen()
        print(f"[LISTENNING] Server is listenning on {self.ip}")

        self.client, addr = self.server.accept()

        self.connected = self.establish_connection()

        thread = threading.Thread(target=self.handle_client, args=(addr,))
        thread.start()

    def handle_client(self, addr: str) -> None:
        if not self.isServer:
            return

        print(f"[NEW CONNECTION] {addr} connected.")

        while self.connected:
            msg = self.read_message()
            if msg is None:
                continue

            print(f"[{addr}] {msg}")

            if msg == self.DISCONNECT_MESSAGE:
                self.connected = False

        # If not connected close the socket
        print("[Terminate] closing connection...")
        self.client.close()

    def cleanup_server(self):
        print("[TERMINATE] Program ended. Starting cleanup...")
        self.send_message(self.DISCONNECT_MESSAGE)
