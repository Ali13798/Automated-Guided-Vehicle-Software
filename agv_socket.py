import atexit
import socket
import threading

from config import read_config


class AgvSocket:
    def __init__(self, ip: str, port: int, isServer: bool = False) -> None:
        """Server or client socket for transmitting messages between the
        AGV and Controller.

        Args:
            ip (str): The IP address of the server/client
            port (int): The Port number of the server/client
            isServer (bool, optional): Dictates whether this object is
                the server or client. Defaults to False.
        """

        # Configuration values
        self.config = read_config()
        self.FORMAT = self.config.socket_encoding_format
        self.HEADERSIZE = self.config.socket_message_header_size
        self.DISCONNECT_MESSAGE = self.config.socket_disconnect_message
        self.HANDSHAKE = self.config.socket_establish_connection_message
        self.MESSAGE_RECEIVED = "!TRANSMITTED"

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
        """Exchanges a handshake message between the server and client.

        Returns:
            bool: True if the handshake was successful, or False otherwise.
        """

        # If the current object is a server.
        if self.isServer:
            self.send_message(self.HANDSHAKE)

            response = self.read_message()
            if response == self.HANDSHAKE:
                return True

            print("[CONN ERROR] Client connection failed.")
            return False

        # If the current object is a client.
        response = self.read_message()
        if response == self.HANDSHAKE:
            self.send_message(self.HANDSHAKE)
            print("[CONN SUCCESS] connected to the Server.")
            return True

        print("[CONN ERROR] did not connect to server.")
        return False

    def read_message(self) -> str | None:
        """Receives a message from the connected socket using a
        header containing the length of the proceedign message.

        Returns:
            str | None: The received message, if not the initial connection.
        """

        try:
            msg_length = self.client.recv(self.HEADERSIZE).decode(self.FORMAT)

            # If the msg_length exists:
            if msg_length:
                msg_length = int(msg_length)
                msg = self.client.recv(msg_length).decode(self.FORMAT)
                return msg

            # If the msg_length does not exist.
            return
        except ConnectionResetError:
            print("Connection forcibly closed.")
            self.connected = False
            return

    def send_message(self, msg: str) -> None:
        """Sends the message to the connected socket using the encoding format
        specified.

        Args:
            msg (str): The message to be transmitted.
        """

        msg_length = len(msg.encode(self.FORMAT))
        send_length = f"{msg_length:<{self.HEADERSIZE}}"

        print(f"[SENDING] length ({msg_length:>3}): {msg}")

        self.client.send(send_length.encode(self.FORMAT))
        self.client.send(msg.encode(self.FORMAT))

    def start_server(self, shared_list: list, mutex: threading.Lock) -> None:
        """Starts the server and waits for client connection."""

        if not self.isServer:
            return

        print("[STARTING] server is starting...")

        self.server.listen()
        print(f"[LISTENNING] Server is listenning on {self.ip}")

        self.client, addr = self.server.accept()

        self.connected = self.establish_connection()

        if not self.connected:
            return

        self.shared_list = shared_list
        self.mutex_shared = mutex

        thread = threading.Thread(target=self.handle_client, args=(addr,))
        thread.start()

    def handle_client(self, addr: tuple[str, int]) -> None:
        """While the client is connected, receives messages from the client.

        Args:
            addr (tuple[str, int]): (IP address, Port number) of the client.
        """

        if not self.isServer:
            return

        print(f"[NEW CONNECTION] {addr} connected.")

        while self.connected:
            msg = self.read_message()
            if msg is None:
                continue

            print(f"[{addr}] {msg}")

            self.mutex_shared.acquire()
            self.shared_list.append(msg)
            self.mutex_shared.release()

            if msg == self.DISCONNECT_MESSAGE:
                self.connected = False

            # The controller sends back response instead.
            # self.send_message(self.MESSAGE_RECEIVED)

        # If not connected close the socket.
        print("[TERMINATE] closing connection...")
        self.client.close()

    def cleanup_server(self) -> None:
        """Sends disconnect message to server if client is
        unexpectedly closed."""

        print("[TERMINATE] Program ended. Starting cleanup...")
        self.send_message(self.DISCONNECT_MESSAGE)


def main():
    return


if __name__ == "__main__":
    main()
