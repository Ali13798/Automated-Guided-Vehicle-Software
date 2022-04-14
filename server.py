import socket
from time import sleep

from agv_socket import AgvSocket
from onboard_controller import Controller


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
