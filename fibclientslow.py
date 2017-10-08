import socket
import time

s = socket.socket()
s.connect(('localhost', 5000))

while True:
    start = time.time()
    s.send(b'30')
    s.recv(256)
    end = time.time()
    print(end - start)
