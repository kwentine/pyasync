""" Use the transport/protocol callback-based API
    - HTTPClientProtocol handles the HTTP exchange and resolves a future when response is complete
    - loop.create_connection() returns a coroutine
    - asyncio.ensure_future() schedules the coroutine to be run
    - we finally run the loop until all futures are resolved, using asyncio.gather()
"""
import asyncio
import socket
import functools

loop = asyncio.get_event_loop()

class HTTPClientProtocol(asyncio.Protocol):
    def __init__(self, host, future):
        self.host = host
        self.future = future
        self.chunks_received = []
        self.response = None
        
    def connection_made(self, transport):
        print('Connection made with: {}'.format(self.host))
        request = 'HEAD / HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(self.host)
        transport.write(request.encode('ascii'))

    def data_received(self, data):
        print('Data received from {}'.format(self.host))
        self.chunks_received.append(data)

    def connection_lost(self, exc):
        response = b''.join(self.chunks_received).decode('utf8')
        self.future.set_result(response)

def main():

    hosts = [
        'facebook.com',
        'news.ycombinator.com',
        'twitter.com',
        'google.com',
        'youtube.com',
        'wikipedia.org',
    ]

    futures = [loop.create_future() for host in hosts]
    
    def protocol_factory(host, f):
        return HTTPClientProtocol(host, f)
    
    for host, f in zip(hosts, futures):
        factory = functools.partial(protocol_factory, host, f)
        coro = loop.create_connection(factory, host, 80)
        asyncio.ensure_future(coro) # Schedule the coroutine

    responses = loop.run_until_complete(asyncio.gather(*futures)) 
    for r in responses:
        print('\n' + r)
    loop.close()
        
if __name__ == "__main__":
    main()
