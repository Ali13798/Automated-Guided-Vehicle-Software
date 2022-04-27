import socket

from tools.agv_socket import AgvSocket


def main():
    PORT = 1234
    # SERVER_IP = socket.gethostbyname(socket.gethostname())
    SERVER_IP = "192.168.0.160"

    client = AgvSocket(ip=SERVER_IP, port=PORT, isServer=False)
    while True:
        text = input("Enter message: ")
        client.send_message(text)
        print(f"[SERVER] {client.read_message()}")


if __name__ == "__main__":
    main()
