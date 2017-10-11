""" Fibonacci server - asyncio - coroutines - low-level socket operations
"""
import socket
import asyncio
from asyncio import coroutine
from concurrent.futures import ThreadPoolExecutor as TPool

loop = asyncio.get_event_loop()
pool = TPool(3)

def fib(n):
    """Compute nth Fibonacci number"""
    if n <= 1: return n
    else: return fib(n-1) + fib(n-2)

def handle_client(conn, addr):
    print('Connection from {}:{}'.format(*addr))
    try:
        while True:
            data = yield from loop.sock_recv(conn, 256)
            if not data:
                break
            n = int(data.decode('ascii'))
            fn = yield from loop.run_in_executor(pool, fib, n) # Run computation in separate thread
            res = str(fn).encode('ascii') + b'\n'
            conn.send(res)
    except Exception as e:
        print('{}:{}'.format(*addr), e, '(closing connection)')
    finally:
        conn.close()

@coroutine    
def start_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False) # Make socket non-blocking
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server running on port %d ..." % port)
    while True:
        conn, addr = yield from loop.sock_accept(s)
        loop.create_task(handle_client(conn, addr))
    
if __name__ == "__main__":
    loop.create_task(start_server())
    loop.run_forever()
