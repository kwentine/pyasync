import socket
from time import sleep
from threading import Thread

n = 0

def monitor():
    """"Print and reset request counter every second"""
    global n
    while True:
        sleep(1)
        print(n, 'req/s')
        n = 0

# Connect to Fibonacci server
s = socket.socket()
s.connect(('localhost', 5000)) 

# Start monitoring to happen in the background
Thread(target=monitor, daemon=True).start()

# Keep sending requests for small fibonacci number
while True:
    s.send(b'10')
    s.recv(256)
    n += 1
