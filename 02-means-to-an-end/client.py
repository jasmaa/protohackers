import socket

HOST = "0.0.0.0"
PORT = 8080


def build_insert_message(timestamp, price):
    buffer = b'I'
    buffer += timestamp.to_bytes(4, byteorder="big", signed=True)
    buffer += price.to_bytes(4, byteorder="big", signed=True)
    return buffer


def build_query_message(mintime, maxtime):
    buffer = b'Q'
    buffer += mintime.to_bytes(4, byteorder="big", signed=True)
    buffer += maxtime.to_bytes(4, byteorder="big", signed=True)
    return buffer


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    s.sendall(build_insert_message(3, 1))
    s.sendall(build_insert_message(1, 1))
    s.sendall(build_insert_message(2, 1))

    s.sendall(build_query_message(1, 3))

    s.sendall(build_insert_message(4, 500))

    s.sendall(build_query_message(1, 5))

    while True:
        data = s.recv(1024)
        print(data)
        if len(data) == 0:
            break
    s.close()
