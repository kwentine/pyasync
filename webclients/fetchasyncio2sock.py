""" Use the following low-level socket operations of the ioloop:
      - sock_recv()
      - sock_sendall()
      - sock_connect()
    This abstracts away the watching/unwatching of socket file descriptors.
"""

import asyncio
import socket

loop = asyncio.get_event_loop()


@asyncio.coroutine
def fetch(host):
    sock = socket.socket()
    sock.setblocking(False)
    yield from loop.sock_connect(sock, (host, 80))
    request = 'GET / HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(host)
    yield from loop.sock_sendall(sock, request.encode('ascii'))
    return (yield from read_all(sock))

@asyncio.coroutine
def read_all(sock):
    response = []
    chunk = yield from loop.sock_recv(sock, 4096)
    while chunk:
        response.append(chunk)
        chunk = yield from loop.sock_recv(sock, 4096)
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

    def print_headers(response):
        headers, body = response.decode('utf8').split('\r\n\r\n')
        print(headers + '\n')

    responses = loop.run_until_complete(main())
    for response in responses:
        print_headers(response)

    loop.close()
