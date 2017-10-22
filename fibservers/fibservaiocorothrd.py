import socket
import asyncio
from fib import fib
from concurrent.futures import ProcessPoolExecutor

loop = asyncio.get_event_loop()
pool = ProcessPoolExecutor(3)

def handle_client(conn):
    while True:
        try:
            data = yield from loop.sock_recv(conn, 256)
            n = int(data.decode('ascii'))
            result = yield from loop.run_in_executor(pool, fib, n) # Run computation in separate thread
            response = str(result).encode('ascii') + b'\n' 
            conn.send(response)
        except:
            break
    conn.close()

def start_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False) # Make socket non-blocking
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server running on port %d ..." % port)
    while True:
        conn, addr = yield from loop.sock_accept(s)
        loop.create_task(handle_client(conn))
    
if __name__ == "__main__":
    loop.create_task(start_server())
    loop.run_forever()
