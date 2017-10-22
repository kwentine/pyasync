from eventloop import *
from concurrent.futures import ThreadPoolExecutor as TPool
from concurrent.futures import ProcessPoolExecutor as PPool
import threading
import socket

pool = PPool(3)

def fib(n):
    """Compute nth Fibonacci number"""
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)

def handle_client(conn):
    """Receive integer from client and send back its square"""
    while True:
        try:
            f = Future()
            def on_data():
                try:
                    f.set_result(conn.recv(256))
                except Exception as e:
                    f.set_exception(e)
            loop.selector.register(conn, EVENT_READ, on_data)
            data = yield from f
            loop.selector.unregister(conn)
            n = int(data.decode('ascii'))
            future = pool.submit(fib, n)
            yield future
            fn = future.result() # This would be a blocking call if future is not resolved
            res = str(fn).encode('ascii') + b'\n'
            conn.send(res)
        except Exception as e:
            print(e)
            conn.close()
            break

@coroutine
def run_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setblocking(False)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server on port %d ..." % port)
    while True:
        f = Future()
        loop.selector.register(s, EVENT_READ, lambda: f.set_result(True))
        yield from f
        loop.selector.unregister(s)
        conn, addr = s.accept() # Blocking
        loop.create_task(handle_client(conn))

if __name__ == "__main__":
    run_server()
    loop.run_forever()
