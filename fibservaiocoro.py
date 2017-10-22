import socket
import asyncio
from fib import fib 

loop = asyncio.get_event_loop()

def handle_client(conn):
    while True:
        try:
            # delegate to loop.sock_recv() coroutine
            # `yield from` expression evaluates to the return value of the coroutine
            data = yield from loop.sock_recv(conn, 256)
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
