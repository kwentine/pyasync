import socket
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from collections import deque

selector = DefaultSelector()

tasks = deque()

def loop():
    while True:
        run_tasks() # Run each task in order, until it suspends before I/O
        events = selector.select() # Poll for sockets that are ready for I/O
        for key, mask in events:
            selector.unregister(key.fileobj)
            tasks.append(key.data) # Queue all tasks whose sockets are ready to go on
             
def run_tasks():
    while tasks:
        try:
            task = tasks.popleft()
            event, sock = next(task) # May raise StopIteration
            selector.register(sock, event, data=task)
        except StopIteration:
            continue
        
def fib(n):
    """Compute nth Fibonacci number"""
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)

def handle_client(conn):
    """Receive integer from client and send back its square"""
    while True:
        yield EVENT_READ, conn # Suspend before reading
        try:
            data = conn.recv(256) 
            n = int(data.decode('ascii'))
            res = str(fib(n)) + '\n'
        except:
            conn.close()
            break
        yield EVENT_WRITE, conn # Suspend before writing
        conn.send(res.encode('ascii'))

def run_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setblocking(False)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server running on port %d ..." % port)
    while True:
        yield EVENT_READ, s # Suspend before reading
        conn, addr = s.accept()
        conn.setblocking(False)
        tasks.append(handle_client(conn))

if __name__ == "__main__":
    tasks.append(run_server())
    loop()
