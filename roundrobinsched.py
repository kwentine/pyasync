# Simple round robin scheduler
from collections import deque

def task1():
    print('Task 1: step1')
    yield
    print('Task 1: step2')
    yield
    print('Task 1: done')
    return 1

def task1():
    print('Task 2: step1')
    yield
    print('Task 2: step2')
    yield
    print('Task 2: done')
    return 1


tasks = deque([countdown(5), countdown(10), countdown(15)])
        
while tasks:
    coro = tasks.popleft()
    try:
        next(coro)
    except StopIteration as exc:
        print('Scheduler: task returned', exc.value)
        continue
    else:
        tasks.append(coro)
