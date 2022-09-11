import json
import socket

HOST = "0.0.0.0"
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'{"method":"isPrime","number":5128215, "extra": "hel')
    s.sendall(b'lo there"}\n')

    s.sendall(
        json.dumps({
            "method": "isPrime",
            "number": 10,
        }).encode("utf8") + b'\n'
        + json.dumps({
            "method": "isPrime",
            "number": 9694333,
        }).encode("utf8") + b'\n'
        + json.dumps({
            "method": "badmethod",
            "number": 23,
        }).encode("utf8") + b'\n'
    )

    while True:
        data = s.recv(1024)
        print(data)
        if len(data) == 0:
            break