import atexit
import socket

from config import read_config

conf = read_config()
FORMAT = conf.socket_encoding_format
HEADERSIZE = conf.socket_message_header_size
DISCONNECT_MESSAGE = conf.socket_disconnect_message
HANDSHAKE = conf.socket_establish_connection_message


class Client:
    def __init__(self, server_ip: str, port: str) -> None:
        self.CLIENT = server_ip
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_ip, port))

        self.connected = self.establish_connection()

        atexit.register(self.cleanup)

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

    def establish_connection(self) -> bool:
        msg = self.read_message()
        if msg == HANDSHAKE:
            self.send_message(HANDSHAKE)
            print("[CONN SUCCESS] connected to the Server.")
            return True

        print("[CONN ERROR] Client connection failed.")
        return False

    def cleanup(self):
        print("[TERMINATE] Program ended. Starting cleanup...")
        self.send_message(DISCONNECT_MESSAGE)


def main():
    PORT = 1234
    CLIENT = socket.gethostbyname(socket.gethostname())

    client = Client(server_ip=CLIENT, port=PORT)

    while True:
        text = input("Enter message: ")
        client.send_message(text)


if __name__ == "__main__":
    main()
