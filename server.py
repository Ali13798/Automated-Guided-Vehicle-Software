import socket
from time import sleep

from onboard_controller.onboard_controller import Controller
from tools.agv_socket import AgvSocket


def main():
    PORT = 1234
    SERVER = socket.gethostbyname(socket.gethostname())

    server = AgvSocket(ip=SERVER, port=PORT, isServer=True)

    ctrl = Controller(server)

    # print("STARTING TO WAIT")

    # for i in range(5):
    #     print("SECOND IS: ", i)
    #     sleep(5)

    # print(ctrl.shared_list)
    # server.start_server()


if __name__ == "__main__":
    main()
