""" Fibonacci server - tornado - TCPServer
"""
from tornado.tcpserver import TCPServer
from tornado import gen
from concurrent.futures import ThreadPoolExecutor as TPool
from tornado.ioloop import IOLoop

pool = TPool(3)

def fib(n):
    """Compute nth Fibonacci number"""
    if n <= 1: return n
    else: return fib(n-1) + fib(n-2)


class FibServer(TCPServer):
    @gen.coroutine
    def handle_stream(self, stream, address):
        print('Connection from {}:{}'.format(*address))
        while True:
            try:
                data = yield stream.read_bytes(256, partial=True)
                n = int(data.decode('ascii'))
                # fn = fib(n)
                fn = yield pool.submit(fib, n)
                res = str(fn).encode('ascii') + b'\n'
                yield stream.write(res)
            except Exception as e:
                print(e)
                break
    
if __name__ == "__main__":
    server = FibServer()
    server.listen(5000, address='localhost')
    print('Fibserver listening on port 5000')
    IOLoop.current().start()
