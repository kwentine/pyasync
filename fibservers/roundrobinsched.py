# Simple round robin scheduler
from collections import deque
from time import sleep

def task1():
    print('Task 1: step1')
    sleep(3)
    yield
    print('Task 1: step2')
    yield
    print('Task 1: done')
    return 1

def task2():
    print('Task 2: step1')
    yield
    print('Task 2: step2')
    yield
    print('Task 2: done')
    return 1

def run_until_complete(tasks):
    while tasks:
        # Fetch next task from the beginning of the queue
        coro = tasks.popleft()
        try:
            # Advance task one step, until next 'yield'
            next(coro)
        except StopIteration as exc:
            # The task finished, and its return value is 
            # retrieved from the exception.
            print('Scheduler: task returned', exc.value)
            continue
        else:
            # Put the task back at the end of the queue
            tasks.append(coro)

if __name__ == "__main__":
    tasks = deque([task1(), task2()])
    run_until_complete(tasks)
