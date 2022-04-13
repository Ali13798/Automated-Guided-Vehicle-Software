import socket

from agv_socket import AgvSocket


def main():
    PORT = 1234
    CLIENT = socket.gethostbyname(socket.gethostname())

    client = AgvSocket(ip=CLIENT, port=PORT, isServer=False)
    while True:
        text = input("Enter message: ")
        client.send_message(text)
        print(f"[SERVER] {client.read_message()}")


if __name__ == "__main__":
    main()
