from fib import fib
import socket
import asyncio

loop = asyncio.get_event_loop()

def start_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False) # Make socket non-blocking
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server running on port %d ..." % port)
    loop.add_reader(s, accept, s)

def accept(sock):
    conn, addr = sock.accept()
    loop.add_reader(conn, handle_client, conn, addr)

def handle_client(conn):
    try:
        data = conn.recv(256)
        n = int(data.decode('ascii'))
        result = fib(n)
        response = str(result).encode('ascii') + b'\n'
        conn.send(response)
    except:
        loop.remove_reader(conn)
        conn.close()
        
if __name__ == "__main__":
    loop.call_soon(start_server)
    loop.run_forever()
