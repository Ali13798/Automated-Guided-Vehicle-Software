import atexit
import socket

FORMAT = "utf-8"
HEADERSIZE = 16
DISCONNECT_MESSAGE = "!DISCONNECT"


class Client:
    def __init__(self, server_ip: str, port: str) -> None:
        self.CLIENT = server_ip
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_ip, port))

        atexit.register(self.cleanup)

    def send_message_to_server(self, msg: str) -> None:
        message = msg.encode(FORMAT)
        msg_length = len(message)

        send_length = f"{msg_length:<{HEADERSIZE}}"
        self.client.send(send_length.encode(FORMAT))
        self.client.send(message)
        print(f"Sending a message of length {msg_length}.")

    # @atexit.register
    def cleanup(self):
        print("Program ended. Starting cleanup...")
        self.send_message_to_server(DISCONNECT_MESSAGE)


def main():
    PORT = 1234
    CLIENT = socket.gethostbyname(socket.gethostname())

    client = Client(server_ip=CLIENT, port=PORT)

    while True:
        text = input("Enter message: ")
        client.send_message_to_server(text)


if __name__ == "__main__":
    main()
