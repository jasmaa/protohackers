import math
import json
import socket
import threading

HOST = "0.0.0.0"
PORT = 8080


class MalformedRequestError(Exception):
    pass


def is_prime(n):
    if n <= 1:
        return False
    if int(n) != n:
        return False
    for i in range(2, int(math.sqrt(n))+1):
        if n % i == 0:
            return False
    return True


def build_response(method, prime):
    return json.dumps({
        "method": method,
        "prime": prime,
    }).encode("utf8") + b'\n'


def build_error_response(error):
    return json.dumps({
        "error": str(error)
    }).encode("utf8") + b'\n'


def process_request(data):
    payload = data.decode("utf8")
    try:
        r = json.loads(payload)
    except json.JSONDecodeError:
        raise MalformedRequestError("could not decode json request")

    if "method" not in r:
        raise MalformedRequestError("missing parameter 'method'")

    if r["method"] == "isPrime":
        if "number" not in r:
            raise MalformedRequestError("missing parameter 'number'")
        if not isinstance(r["number"], int) and not isinstance(r["number"], float) or isinstance(r["number"], bool):
            # bool is int in Python :(
            raise MalformedRequestError("number was not a number")
        prime = is_prime(r["number"])
        response = build_response(r["method"], prime)
        return response
    else:
        raise MalformedRequestError("method not supported")


def handle_client(conn, addr):
    with conn:
        buffer = b''
        while True:
            data = conn.recv(1024)
            print(f"{addr}: Received {data}")
            if len(data) == 0:
                break
            start = 0
            for i in range(len(data)):
                if data[i] == ord("\n"):
                    buffer += data[start:i+1]
                    start = i + 1
                    try:
                        print(f"{addr}: Processing {buffer}")
                        conn.sendall(process_request(buffer))
                        buffer = b''
                    except MalformedRequestError as e:
                        response = build_error_response(e)
                        conn.sendall(response)
                        return
            buffer += data[start:]


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
