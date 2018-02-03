from tornado.gen import coroutine
from tornado.ioloop import IOLoop

def genfunc():
    yield
    return 1

@coroutine
def tdcoro():
    yield
    return 2

@coroutine
def main():

    # Yield nothing, which evaluates to None
    res = (yield)
    print('Result: %r' % res)

    # Delegate to a native generator
    res = yield from genfunc()
    # But not:
    #   `yield genfunc()`
    # This would raise a `BadYieldError: yielded unknown object <generator object genfunc at ...>
    print('Result: %s' % res)

    # Yield a decorated native coroutine, which evaluates the value it will return when run to exhaustion.
    res = yield tdcoro()
    # But not:
    #   `yield from tdcoro()`
    # This would raise a `TypeError: 'Future' object not iterable`

    print('Result: %s' % res)

if __name__ == "__main__":
    IOLoop.current().run_sync(main)