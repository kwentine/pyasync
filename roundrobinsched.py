# Simple round robin scheduler
from collections import deque

def countdown(n):
    print('Counting down from', n)
    while n:
        yield n
        n -= 1

tasks = deque([countdown(5), countdown(10), countdown(15)])
        
while tasks:
    coro = tasks.popleft()
    try:
        result = next(coro)
        print(result)
    except StopIteration:
        continue
    else:
        tasks.append(coro)
