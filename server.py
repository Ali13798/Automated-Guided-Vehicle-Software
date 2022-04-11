import socket
import threading

PORT = 1234
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = "utf-8"
HEADERSIZE = 16
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))


def handle_client(client: socket.socket, addr):
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

    client.close()


def start():
    server.listen()
    print(f"[LISTENNING] Server is listenning on {SERVER}")
    while True:
        client, addr = server.accept()
        thread = threading.Thread(
            target=handle_client, args=(client, addr), daemon=True
        )
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()
