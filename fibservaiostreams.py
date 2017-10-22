import socket
import asyncio
from fib import fib
from concurrent.futures import ThreadPoolExecutor

loop = asyncio.get_event_loop()
pool = ThreadPoolExecutor(3)

def handle_client(reader, writer):
    while True:
        try:
            data = yield from reader.read(256)
            if not data:
                break
            n = int(data.decode('ascii'))
            fn = yield from loop.run_in_executor(pool, fib, n) # Run computation in separate thread
            res = str(fn).encode('ascii') + b'\n'
            writer.write(res)
        except:
            break
    writer.close()
    
if __name__ == "__main__":
    server_coro = asyncio.start_server(handle_client, host='127.0.0.1', port=5000)
    loop.create_task(server_coro)
    loop.run_forever()


