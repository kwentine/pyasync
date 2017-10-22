""" Implement fetch using the ioloop file descriptor methods
    - loop.add_reader() / loop.remove_reader()
    - loop.add_writer() / loop.remove_writer()
"""
import asyncio
import socket

loop = asyncio.get_event_loop()

@asyncio.coroutine
def fetch(host):
    sock = yield from connect(host, 80)
    request = 'GET / HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(host)
    sock.send(request.encode('utf8'))
    return (yield from read_all(sock))

@asyncio.coroutine
def connect(host, port):
    sock = socket.socket()
    sock.setblocking(False)
    try:
        sock.connect((host, port))
    except BlockingIOError:
        pass
    f = loop.create_future()
    def on_connected():
        print('Connected to {}'.format(host))
        loop.remove_writer(sock)
        f.set_result(sock)
    loop.add_writer(sock, on_connected)
    return (yield from f)

@asyncio.coroutine
def read(sock):
    f = loop.create_future()
    def on_readable():
        loop.remove_reader(sock)
        f.set_result(sock.recv(4096))
    loop.add_reader(sock, on_readable)
    return (yield from f)

@asyncio.coroutine
def read_all(sock):
    response = []
    chunk = yield from read(sock)
    while chunk:
        response.append(chunk)
        chunk = yield from read(sock)
    return b''.join(response)

@asyncio.coroutine
def main():
    
    hosts = [
        'facebook.com',
        'news.ycombinator.com',
        'twitter.com',
        'google.com',
        'youtube.com',
        'wikipedia.org',
    ]
    
    done, pending = yield from asyncio.wait([fetch(host) for host in hosts])
    return map(lambda f: f.result(), done)

if __name__ == "__main__":
    responses = loop.run_until_complete(main())
    for response in responses:
        headers, body = response.decode('utf8').split('\r\n\r\n')
        print(headers + '\n')
    loop.close()
