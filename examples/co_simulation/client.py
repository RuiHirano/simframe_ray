import socket
import pickle

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 8001))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

full_msg = b''
while True:
    msg = s.recv(4096)
    if len(msg) <= 0:
        break
    full_msg += msg
d = pickle.loads(full_msg)
print(d)