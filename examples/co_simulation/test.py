import socket
import pickle
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("localhost", 1235))  # IPとポート番号を指定します
s.listen(5)

data = {1: "Apple", 2: "Orange"}
while True:
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")
    msg = pickle.dumps(data)
    clientsocket.send(msg)
    clientsocket.close()