import socket
import threading

HOST = "0.0.0.0"
PORT = 8080


def handle_client(conn, addr):
    with conn:
        while True:
            data = conn.recv(1024)
            print(f"{addr}: Received {data}")
            if len(data) == 0:
                break
            conn.sendall(data)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Started server on port {PORT}...")
        while True:
            conn, addr = s.accept()
            print(f"Connected to {addr}!")
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()
