import sys
import tornado.ioloop
from tornado.httpclient import HTTPClient, AsyncHTTPClient
from tornado.concurrent import Future
from tornado import gen
from datetime import datetime
from time import sleep
from concurrent.futures import ThreadPoolExecutor

URLS = [
    'http://facebook.com/',
    'http://news.ycombinator.com',
    'http://twitter.com/',
    'http://google.com/',
    'http://youtube.com/',
    'http://wikipedia.org/'
]          

TODO = 0

def timed(func):
    def wrapped(*args, **kwargs):
        start = datetime.now()
        print("%s:start" % func.__name__)
        func(*args, **kwargs)
        end = datetime.now()
        dt = end - start
        name = func.__name__
        print("%s:end %s" % (dt, name))
    return wrapped

def print_size(response):
    url = response.request.url
    length = int(len(response.body) / 1024)
    print('{url} : {length} Kb'.format(url=url, length=length))

def sync_fetch(url):
    http_client = HTTPClient()
    response = http_client.fetch(url)
    return response

def async_fetch(url, callback):
    http_client = AsyncHTTPClient()
    def handle_response(response):
        callback(response)
    http_client.fetch(url, callback=handle_response)

def async_fetch_future(url):
    http_client = AsyncHTTPClient()
    fetch_future = http_client.fetch(url)
    return fetch_future

@gen.coroutine
def async_fetch_coroutine(url):
    print('Fetching', url)
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    return response


# Fetch the URL and print the response, before fetching the next.
@timed
def main_sync():
    for url in URLS:
        print_size(sync_fetch(url))

# The two following implementations asynchronously fetch all URLS,
# printing results as soone as they arrive. Running several times will
# likely show results printed in different order
def main_async():
    for url in URLS:
        async_fetch(url, print_size)

def main_async_future():
    print('Enter')
    for url in URLS:
        f = async_fetch_future(url)
        f.add_done_callback(lambda f: print_size(f.result()))
    print('Exit')


# Fetches url one after the other
# Next url is fetched when result of previous fetch
# has been processed. Basically synchronous behavior
@gen.coroutine
def main_async_coroutine():
    print('Enter coroutine')
    for url in URLS:
        response = yield async_fetch_coroutine(url)
        print_size(response)
    print('Exit coroutine')
    return

# Fetches all urls in parallel
# Prints the results when all have responded
@gen.coroutine
def main_async_coroutine_2():
    print('Enter coroutine')
    responses = yield [async_fetch_coroutine(url) for url in URLS]
    for response in responses:
        print_size(response)
    print('Exit coroutine')
    return


# Uses ThreadPoolExecutor with blocking function
# .submit() returns a coroutine-compatible future
@gen.coroutine
def main_threaded():
    print('Enter threaded')
    thread_pool = ThreadPoolExecutor(6)
    responses = yield [thread_pool.submit(sync_fetch, url) for url in URLS]
    for response in responses:
        print_size(response)
    print('Exit threaded')

def main_threaded_2():
    print('Enter threaded')
    thread_pool = ThreadPoolExecutor(6)
    for url in URLS:
        future = thread_pool.submit(sync_fetch, url)
        future.add_done_callback(lambda f: print_size(f.result()))
    print('Exit threaded')

@gen.coroutine
def periodic_cb(cb=lambda: print('Hello')):
    print('Enter')
    while True:
        cb()
        yield gen.sleep(1)
    print('Exit')

if __name__ == "__main__":
    loop = tornado.ioloop.IOLoop.current()
    # loop.run_sync(main_async)
    # loop.run_sync(main_async_coroutine_2)
    # loop.run_sync(main_threaded)
    # loop.run_sync(main_threaded_2)
    # loop.run_sync(periodic_cb)
    # main_async()
    # main_async_future()
    # main_threaded_2()
    # loop.spawn_callback(periodic_cb)
    loop.start()

