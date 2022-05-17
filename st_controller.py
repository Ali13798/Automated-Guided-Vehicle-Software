"""
File:       st_controller.py
Author:     Ali Karimiafshar
"""

from stationary_controller.stationary_controller_gui import GUI
from tools.agv_socket import AgvSocket


def main_old():
    PORT = 1234
    # SERVER_IP = socket.gethostbyname(socket.gethostname() + ".local")
    SERVER_IP = "192.168.0.160"

    client = AgvSocket(ip=SERVER_IP, port=PORT, isServer=False)
    while True:
        text = input("Enter message: ")
        client.send_message(text)
        print(f"[SERVER] {client.read_message()}")


def main():
    GUI().mainloop()


if __name__ == "__main__":
    main()
