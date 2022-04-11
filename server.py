import socket

from agv_socket import AgvSocket


def main():
    PORT = 1234
    SERVER = socket.gethostbyname(socket.gethostname())

    server = AgvSocket(ip=SERVER, port=PORT, isServer=True)

    server.start_server()


if __name__ == "__main__":
    main()
