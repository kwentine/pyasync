import sys
import socket
import time

s = socket.socket()
s.connect(('localhost', 5000))

n = sys.argv[1] if len(sys.argv) > 1 else 30

while True:
    start = time.time()
    s.send(str(n).encode('ascii'))
    s.recv(256)
    end = time.time()
    print(end - start)
