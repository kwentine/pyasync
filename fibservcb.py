import socket
from fib import fib
from selectors import DefaultSelector, EVENT_READ
selector = DefaultSelector()

def start_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server running on port %d ..." % port)
    # Register callback for when a connection arrives
    selector.register(s, EVENT_READ, data=accept)

def accept(sock):
    conn, addr = sock.accept()
    # Register callback for when client data arrives
    selector.register(conn, EVENT_READ, handle_client)

def handle_client(conn):
    try: 
        data = conn.recv(256)
        n = int(data.decode('ascii'))
        result = fib(n)
        response = str(result).encode('ascii') + b'\n'
        conn.send(response)
    except:
        selector.unregister(conn)
        conn.close()

def loop():
    while True:
        # Blocks until a registered socket is ready for I/O
        events = selector.select()
        for key, mask in events:
            # key.fileobj : registered socket
            # key.data    : associated callback
            callback = key.data
            callback(key.fileobj) 
    
if __name__ == "__main__":
    start_server()
    loop()
