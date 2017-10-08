import socket
from time import sleep
from threading import Thread

n = 0

def monitor():
    global n
    while True:
        sleep(1)
        print(n, 'req/s')
        n = 0

s = socket.socket()
s.connect(('localhost', 5000))

Thread(target=monitor, daemon=True).start()
while True:
    s.send(b'10')
    s.recv(256)
    n += 1
