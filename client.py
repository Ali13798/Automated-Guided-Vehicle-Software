import socket

PORT = 1234
host_name = socket.gethostname()
IP = socket.gethostbyname(host_name)
FORMAT = "utf-8"
HEADERSIZE = 16
DISCONNECT_MESSAGE = "!DISCONNECT"


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP, PORT))


def send_message(msg: str) -> None:
    message = msg.encode(FORMAT)
    msg_length = len(message)

    send_length = f"{msg_length:<{HEADERSIZE}}".encode(FORMAT)
    client.send(send_length)
    client.send(message)
    print(send_length)


while True:
    text = input("Enter message: ")
    send_message(text)
