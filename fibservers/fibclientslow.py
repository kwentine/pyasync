import sys
import socket
import time

# Which Fibonacci number to ask for
# Controls the burden we want to put on the server
n = sys.argv[1] if len(sys.argv) > 1 else 33

# Connect to Fibserver
s = socket.socket()
s.connect(('localhost', 5000))

while True:
    # Send request and log the time it takes to complete.
    start = time.time()
    s.send(str(n).encode('ascii'))
    s.recv(256)
    end = time.time()
    print(end - start)
