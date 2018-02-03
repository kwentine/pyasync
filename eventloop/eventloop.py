from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from types import GeneratorType

# Possible states a future can be in
_PENDING = 'PENDING'
_FINISHED = 'FINISHED' 
_CANCELLED = 'CANCELLED' # Not used in this simplified implementation


class InvalidStateError(Exception):
    """Operation not allowed in this state"""


class Future:
    """Promise of a future value
    """
    
    _STATE = _PENDING
    _result = None
    _exception = None

    def __init__(self):
        self._callbacks = []

    def done(self):
        return self._STATE != _PENDING

    def result(self):
        if self._STATE != _FINISHED:
            raise InvalidStateError('Result is not ready')
        if self._exception is not None:
            raise self._exception
        return self._result
    
    def __iter__(self):
        if not self.done():
            yield self
        return self.result()

    def add_done_callback(self, fn):
        """ Schedule a callback to be called when the future resolves.

        If the future is resolved, call it immediatly.
        """
        if self._STATE == _FINISHED:
        # Here, schedule callback on the event loop
            fn(self)
        else:
            self._callbacks.append(fn)

    def set_result(self, result):
        """Mark Future done and set its result"""

        # A result can only be set on a pending future
        if self._STATE != _PENDING:
            raise InvalidStateError('Setting result on non-pending Future')
        self._result = result
        self._STATE = _FINISHED

        # Run callbacks
        self._schedule_callbacks()

    def set_exception(self, exc):
        assert isinstance(exc, Exception), 'must be exception instance'
        self._exception = exc
        
    def _schedule_callbacks(self):
        """Run callbacks with self as single argument.

        In asyncio, callbacks are not ran immediately but scheduled on the event loop.
        """
        for callback in self._callbacks:
            callback(self)
        self._callbacks[:] = []
        
class Task(Future):
    """Coroutine wrapped in a future

    Conventions:
    - Only futures can be yielded directly
    - Delegation to sub-generators is made using `yield from`
    - As a convenience, futures are made iterable so they can be used w/ `yield from` as well
    """
    def __init__(self, coro, loop=None):
        # TODO Instanciate a task with the thread's default IOLoop another one is explicitly passed
        super().__init__()
        self._coro = coro
        self._loop = loop

    def _step(self, sendval=None):
        """Advance coroutine one step
        """
        # TODO Handle other possible types of yielded values
        #     - A list of futures
        try:
            result = self._coro.send(sendval)
            # 1. If a coroutine was yielded, wrap it in a future
            if isinstance(result, GeneratorType):
                result = Task(result)

            # 2. If we now have a future, register ourselves to be woken up when it is resolved
            if isinstance(result, Future):
                result.add_done_callback(self._wakeup)
                # 3. The future may need the event loop to advance it towards resolution
                if isinstance(result, Task):
                    self._loop.add_callback(result)
            else:
                self._loop.add_callback(self._wakeup)
        except StopIteration as exc:
            self.set_result(exc.value)

    def _wakeup(self, future=None):
        # If awaken by a future that got resolved, feed its result to the coroutine
        sendval = future.result() if future is not None else None
        self._step(sendval)


class EventLoop:

    def __init__(self):
        self.selector = DefaultSelector()
        self._stopping = False
        
    def run_until_complete(self, future):
        """Run a Future until completion and return its result"""
        def run_until_complete_cb(future):
            self._stopping = True
        future.add_done_callback(run_until_complete_cb)
        self.run_forever()
        return future.result()

    def run_forever(self):
        while not self._stopping:
            events = self.selector.select()
            for key, event in events:
                callback = key.data
                callback()

    def create_task(self, coro):
        """Schedule a coroutine object
        
        Return a Task object
        """
        task = Task(coro)
        # Needed here, but not in original source code where instead,
        # a task schedules `_step()` to be called soon at
        # instanciation. See asyncio/tasks.py Task/.__init__
        task._step() 
        return task

loop = EventLoop()
                
def coroutine(gen_func):
    """Decorator function that wraps coroutine into a task."""
    def wrapped(*args, **kwargs):
        coro = gen_func(*args, **kwargs)
        return loop.create_task(coro)
    return wrapped

@coroutine
def wait(futures):
    f = Future()
    def all_done(future):
        if all(map(lambda f: f.done(), futures)):
            results = map(lambda f: f.result(), futures)
            f.set_result(results)
    for future in futures:
        future.add_done_callback(all_done)
    return (yield from f)

def ensure_future(coro_or_future):
    """ 
    Future -> return it
    Coroutine -> wrap in a task 
    """
    pass


