from fib import fib
from eventloop import *
import socket

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
            res = str(fib(n)).encode('ascii') + b'\n'
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
