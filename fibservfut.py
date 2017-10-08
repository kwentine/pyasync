import socket
import select
from collections import deque
from concurrent.futures import ProcessPoolExecutor as Pool

pool = Pool(5)

ready = deque()
read_wait = {}
write_wait = {}
future_wait = {}

future_notify, future_event = socket.socketpair()

def loop():
    while True:
        run_tasks()
        if read_wait or write_wait:
            read, write, _ = select.select(read_wait, write_wait, []) # Blocking
            schedule_io(read, write)

def run_tasks():
    while ready:
        try:
            task = ready.popleft()
            why, what = next(task)
            wait_for_io(why, what, task)
        except StopIteration:
            continue

def wait_for_io(why, what, task):
    if why == 'read':
        read_wait[what.fileno()] = task
    elif why == 'write':
        write_wait[what.fileno()] = task
    elif why == 'future':       
        future_wait[what] = task
        what.add_done_callback(future_ready)


def future_monitor():
    while True:
        yield 'read', future_event
        future_event.recv(256)

def future_ready(f):
    schedule(future_wait.pop(f))
    future_notify.send(b'1') # Unblock the polling
        
def schedule_io(read, write):
    for sock in read:
        schedule(read_wait.pop(sock))
    for sock in write:
        schedule(write_wait.pop(sock))
        
def schedule(task):
    ready.append(task)

def fib(n):
    """Compute nth Fibonacci number"""
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)

def handle_client(conn):
    """Receive integer from client and send back its square"""
    while True:
        yield 'read', conn # Suspend before reading
        try:
            data = conn.recv(256) 
            n = int(data.decode('ascii'))
        except:
            conn.close()
            break
        future = pool.submit(fib, n)
        yield 'future', future
        res = str(future.result()) + '\n'
        yield 'write', conn # Suspend before writing
        conn.send(res.encode('ascii'))

def run_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server on port %d ..." % port)
    while True:
        yield 'read', s # Suspend before reading
        conn, addr = s.accept() 
        schedule(handle_client(conn))

if __name__ == "__main__":
    schedule(future_monitor())
    schedule(run_server())
    loop()
