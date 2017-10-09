import socket
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

selector = DefaultSelector()

def fib(n):
    """Compute nth Fibonacci number"""
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)

def handle_client(conn):
    # Socket ready for reading
    try: 
        data = conn.recv(256)
        if not data:
            raise Exception('Connection closed by {}:{}'.format(*conn.getpeername()))
        n = int(data.decode('ascii'))
        res = str(fib(n)).encode('ascii') + b'\n'
        conn.send(res)
    except Exception as e:
        print(e)
        selector.unregister(conn)
        conn.close()
    
def accept(sock):
    conn, addr = sock.accept()
    print('Connection from {}:{}'.format(*addr))
    selector.register(conn, EVENT_READ, handle_client)

def start_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False) # Make socket non-blocking
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server running on port %d ..." % port)
    selector.register(s, EVENT_READ, data=accept)

def loop():
    while True:
        events = selector.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj)
    
if __name__ == "__main__":
    start_server()
    loop()
