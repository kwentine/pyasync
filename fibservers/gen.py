def simple_coroutine():
    print('Step 1')
    yield
    print('Step 2')
    yield
    return 'Done'

def countdown(n):
    print('Counting down from', n)
    while n > 0:
        yield n
        n -= 1
    return 'Done counting.'

def countdown_twice(n):
    yield from countdown(n)
    yield from countdown(n)
    return 'Done counting twice'

