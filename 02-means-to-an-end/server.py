import socket
import threading

HOST = "0.0.0.0"
PORT = 8080

addr2asset = {}


class BST:
    class Node:
        def __init__(self, key, value):
            self.left = None
            self.right = None
            self.key = key
            self.value = value

        def __str__(self):
            return f"({str(self.left)}, {self.key}:{self.value}, {str(self.right)})"

    def __init__(self):
        self.root = None

    def insert(self, key, value):
        if self.root == None:
            self.root = BST.Node(key, value)
        else:
            def helper(curr, key, value):
                if curr == None:
                    return
                elif key < curr.key:
                    if curr.left == None:
                        curr.left = BST.Node(key, value)
                    else:
                        helper(curr.left, key, value)
                else:
                    if curr.right == None:
                        curr.right = BST.Node(key, value)
                    else:
                        helper(curr.right, key, value)
            helper(self.root, key, value)

    def query(self, minkey, maxkey):
        values = []
        if self.root == None:
            return values
        else:
            def helper(curr, minkey, maxkey):
                if curr == None:
                    return
                if curr.key >= minkey:
                    helper(curr.left, minkey, maxkey)
                if curr.key >= minkey and curr.key <= maxkey:
                    values.append(curr.value)
                if curr.key <= maxkey:
                    helper(curr.right, minkey, maxkey)
            helper(self.root, minkey, maxkey)
            return values


class ParseError(Exception):
    pass


class InsertMessage:
    def __init__(self, timestamp, price):
        self.timestamp = timestamp
        self.price = price

    def build_message(self):
        buffer = b''
        buffer += ord("I")
        buffer += self.timestamp.to_bytes(4, byteorder="big", signed=True)
        buffer += self.price.to_bytes(4, byteorder="big", signed=True)
        return buffer

    @staticmethod
    def parse_message(data):
        if data[0] != ord("I"):
            raise ParseError("incorrect method")
        return InsertMessage(
            int.from_bytes(data[1:5], byteorder="big", signed=True),
            int.from_bytes(data[5:9], byteorder="big", signed=True),
        )


class QueryMessage:
    def __init__(self, mintime, maxtime):
        self.mintime = mintime
        self.maxtime = maxtime

    def build_message(self):
        buffer = b''
        buffer += ord("Q")
        buffer += self.mintime.to_bytes(4, byteorder="big", signed=True)
        buffer += self.maxtime.to_bytes(4, byteorder="big", signed=True)
        return buffer

    @staticmethod
    def parse_message(data):
        if data[0] != ord("Q"):
            raise ParseError("incorrect method")
        return QueryMessage(
            int.from_bytes(data[1:5], byteorder="big", signed=True),
            int.from_bytes(data[5:9], byteorder="big", signed=True),
        )


def process_message(conn, addr, buffer):
    if buffer[0] == ord("I"):
        msg = InsertMessage.parse_message(buffer)
        print(f"{addr}: Inserting {msg.price} at t={msg.timestamp}")
        addr2asset[addr].insert(msg.timestamp, msg.price)
    elif buffer[0] == ord("Q"):
        msg = QueryMessage.parse_message(buffer)
        prices = addr2asset[addr].query(msg.mintime, msg.maxtime)
        print(f"{addr}: Querying t=[{msg.mintime}, {msg.maxtime}]")
        print(f"{addr}: {sum(prices)}/{len(prices)}")
        m = int(sum(prices) / len(prices)) if len(prices) > 0 else 0
        conn.sendall(int.to_bytes(m, 4, byteorder="big", signed=True))


def handle_client(conn, addr):
    with conn:
        if addr not in addr2asset:
            addr2asset[addr] = BST()

        buffer = bytearray(9)
        idx = 0
        while True:
            data = conn.recv(1024)
            print(f"{addr}: Received {data}")
            if len(data) == 0:
                break
            for c in data:
                buffer[idx] = c
                idx += 1
                if idx == 9:
                    process_message(conn, addr, buffer)
                    idx = 0


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
