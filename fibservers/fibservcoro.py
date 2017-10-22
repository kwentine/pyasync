import socket
from fib import fib
from selectors import DefaultSelector, EVENT_READ
from collections import deque

selector = DefaultSelector()

tasks = deque()

def loop():
    while True:
        run_tasks() # Run each task in order, advancing it until next 'yield'
        events = selector.select() # Poll for sockets that are ready for I/O
        for key, mask in events:
            selector.unregister(key.fileobj)
            tasks.append(key.data) # Queue all tasks whose sockets are ready to go on
             
def run_tasks():
    """Advance each queued coroutine one step
    
    Each coroutine is assumed to suspend before I/O, yielding the
    socket it is interested to read from. 
    """
    
    while tasks:
        try:
            task = tasks.popleft()
            event, sock = next(task) 
            selector.register(sock, event, data=task) 
        except StopIteration:  # Exception raised when a coroutine has reached its end by returning
            continue
        
def handle_client(conn):
    
    while True:
        try:
            yield EVENT_READ, conn # Suspend before reading
            data = conn.recv(256) 
            n = int(data.decode('ascii'))
            result = fib(n) 
            response = str(result).encode('ascii') + b'\n'
            conn.send(response) 
        except:
            break
    print('Client disconnected')
    conn.close()


def start_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server running on port %d ..." % port)
    while True:
        yield EVENT_READ, s # Suspend until socket is ready to read
        conn, addr = s.accept()
        new_task = handle_client(conn) # This creates a coroutine object
        tasks.append(new_task) 

if __name__ == "__main__":
    tasks.append(start_server())
    loop() # Start the event loop
