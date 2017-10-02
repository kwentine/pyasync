""" Use the streams coroutine-based API
    - asyncio.open_connection() (analogous to create_connection())
    - reader.read() (or readuntil())
    - writer.write()
"""

import asyncio
import socket

loop = asyncio.get_event_loop()


@asyncio.coroutine
def fetch(host):
    reader, writer = yield from asyncio.open_connection(host, port=80)
    request = 'GET / HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(host)
    writer.write(request.encode('ascii'))
    return (yield from reader.readuntil(separator=b'\r\n\r\n'))

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
    responses = [r.decode('utf8') for r in loop.run_until_complete(main())]
    print('\n'.join(responses))
    loop.close()
