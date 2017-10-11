""" Fibonacci server - asyncio - streams 
"""
import socket
import asyncio
from asyncio import coroutine
from concurrent.futures import ThreadPoolExecutor as TPool

loop = asyncio.get_event_loop()
pool = TPool(3)

def fib(n):
    """Compute nth Fibonacci number"""
    if n <= 1: return n
    else: return fib(n-1) + fib(n-2)

def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print('Connection from {}:{}'.format(*addr))
    try:
        while True:
            data = yield from reader.read(256)
            if not data:
                break
            n = int(data.decode('ascii'))
            fn = yield from loop.run_in_executor(pool, fib, n) # Run computation in separate thread
            res = str(fn).encode('ascii') + b'\n'
            writer.write(res)
    except Exception as e:
        print('{}:{}'.format(*addr), e)
    finally:
        writer.close()
    
if __name__ == "__main__":
    coro = asyncio.start_server(handle_client, host='127.0.0.1', port=5000)
    # Get a handle on the server returned by the coroutine,
    # used below to gracefully handle server interruption
    server = loop.run_until_complete(coro) 
    print("Fibonacci server running on {}".format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


