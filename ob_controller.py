import socket
from time import sleep

from onboard_controller.controller import Controller
from tools.agv_socket import AgvSocket


def main():
    PORT = 1234
    SERVER = socket.gethostbyname(socket.gethostname() + ".local")

    server = AgvSocket(ip=SERVER, port=PORT, isServer=True)

    ctrl = Controller(server)

    input()


if __name__ == "__main__":
    main()
