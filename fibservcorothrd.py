import socket
import functools
from fib import fib
from selectors import DefaultSelector, EVENT_READ
from concurrent.futures import ThreadPoolExecutor
from collections import deque

tasks = deque()
selector = DefaultSelector()
pool = ThreadPoolExecutor(2)


# Event loop is unchanged from fibservcoro.py
def loop():
    while True:
        run_tasks() # Run each task in order, advancing it until next 'yield'
        events = selector.select() # Poll for sockets that are ready for I/O
        for key, mask in events:
            selector.unregister(key.fileobj)
            tasks.append(key.data) # Queue all tasks whose sockets are ready to go on

            
def handle_client(conn):
    while True:
        try:
            yield EVENT_READ, conn # Suspend until data arrives from the client
            data = conn.recv(256)
            n = int(data.decode('ascii'))
            future = pool.submit(fib, n) # Compute Fibonacci in another thread.
            yield 'future', future       # Suspend until the computation is done
            result = future.result()     # Result is now available
            response = str(result).encode('ascii') + b'\n' 
            conn.send(response)
        except:
            break
    conn.close()
    print('Client disconnected')

def run_tasks():
    while tasks:
        try:
            task = tasks.popleft()
            event, awaited = next(task) 
            if event == 'future':
                # Create a pair of connected sockets:
                #
                #  - the first will be used by the future to notify
                # that it is ready,
                # 
                #   - the second will be registered in the selector
                # with the task to resume.
                notifier, notified = socket.socketpair()
                callback = functools.partial(on_future_done, notifier)
                awaited.add_done_callback(callback)

                # Register the socket that will be notified, with the
                # task to resume.
                selector.register(notified, EVENT_READ, data=task)
            else:
                selector.register(awaited, event, data=task)
        except StopIteration:
            continue

# Function called by Futures when their result is ready. The future
# passes itself as a single argument to its callbacks, which is why
# the second argument is mandatory. The first one will be bound by
# functools.partial
def on_future_done(notifier, future):
    # Notify that the future's result is ready by
    # sending a message to the other end.
    notifier.send(b'1') 
    notifier.close()

# run_server is unchanged from fibservcoro.py
def run_server(host='127.0.0.1', port=5000): 
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
    tasks.append(run_server())
    loop()
