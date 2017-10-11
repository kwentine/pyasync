""" Fibonacci server - asyncio - file descriptors - callbacks
"""
import socket
import asyncio
loop = asyncio.get_event_loop()

def fib(n):
    """Compute nth Fibonacci number"""
    if n <= 1: return n
    else: return fib(n-1) + fib(n-2)

def handle_client(conn, addr):
    try:
        # Socket ready for reading
        data = conn.recv(256)
        if not data:
            raise Exception('Empty data')
        n = int(data.decode('ascii'))
        res = str(fib(n)).encode('ascii') + b'\n'
        conn.send(res)
    except Exception as e:
        print('{}:{}'.format(*addr), e, '(closing connection)')
        loop.remove_reader(conn) # Remove reader
        conn.close()
    
def accept(sock):
    conn, addr = sock.accept()
    print('Connection from {}:{}'.format(*addr))
    loop.add_reader(conn, handle_client, conn, addr)

def start_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False) # Make socket non-blocking
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server running on port %d ..." % port)
    loop.add_reader(
        s,      # File descriptor to watch for reading
        accept, # Callback
        s       # Arguments to pass to callback
    )
    
if __name__ == "__main__":
    loop.call_soon(start_server)
    loop.run_forever()
