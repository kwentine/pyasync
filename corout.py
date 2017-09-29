from tornado import gen
import tornado.ioloop


# Broken : I can yield only futures to the engine

@gen.coroutine
def countdown(n):
    while n:
        yield n
        n -= 1

def main():
    future = yield countdown(10)
    future.add_done_callback(lambda f: print(f.result()))


loop = tornado.ioloop.IOLoop.current()
loop.run_sync(main)
loop.start()
