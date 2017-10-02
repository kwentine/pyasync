from eventloop import Future, Task, coroutine, loop, wait
from selectors import EVENT_READ, EVENT_WRITE
import socket

@coroutine
def fetch(host):
    sock = yield from connect(host, 80)
    request = 'GET / HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(host)
    sock.send(request.encode('utf8'))
    response = yield from read_all(sock)
    return response

def connect(host, port):
    sock = socket.socket()
    sock.setblocking(False)
    try:
        sock.connect((host, port))
    except BlockingIOError:
        pass
    f = Future()
    def on_connected():
        f.set_result(True)
    loop.selector.register(sock, EVENT_WRITE, data=on_connected)
    yield from f
    loop.selector.unregister(sock)
    return sock

def read(sock):
    f = Future()
    def on_readable():
        f.set_result(sock.recv(4096))
    loop.selector.register(sock, EVENT_READ, on_readable)
    chunk = yield from f
    loop.selector.unregister(sock)
    return chunk

def read_all(sock):
    response = []
    chunk = yield from read(sock)
    while chunk:
        response.append(chunk)
        chunk = yield from read(sock)
    return b''.join(response)    

if __name__ == "__main__":
    t1 = fetch('www.dabeaz.com')
    t2 = fetch('www.liberation.fr')
    responses = loop.run_until_complete(wait([t1, t2]))
    for r in responses:
        print('Response: {}'.format(len(r)))
