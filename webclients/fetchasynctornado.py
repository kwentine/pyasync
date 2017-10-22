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

def fetch_sync(url):
    http_client = HTTPClient()
    response = http_client.fetch(url)
    return response

def fetch_async_cb(url, callback):
    http_client = AsyncHTTPClient()
    def handle_response(response):
        callback(response)
    http_client.fetch(url, callback=handle_response)

def fetch_async_future(url):
    http_client = AsyncHTTPClient()
    fetch_future = http_client.fetch(url)
    return fetch_future

@gen.coroutine
def fetch_async_coro(url):
    print('Fetching', url)
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    return response


# We now illustrate how to fetch a sequence of urls using these
# different approaches.

def print_size(response):
    """Print the size of the response and the URL it was fetched from"""
    
    url = response.request.url
    length = int(len(response.body) / 1024)
    print('{url} : {length} Kb'.format(url=url, length=length))

# Fetch the URL and print the response, before fetching the next.
def main_sync():
    for url in URLS:
        print_size(sync_fetch(url))

# The two following implementations asynchronously fetch all URLS,
# printing results as soone as they arrive. Running several times will
# likely show results printed in different order
def main_async():
    for url in URLS:
        fetch_async_cb(url, print_size)

def main_async_future():
    print('Enter')
    for url in URLS:
        f = fetch_async_future(url)
        f.add_done_callback(lambda f: print_size(f.result()))
    print('Exit')


# Fetches url one after the other
# Next url is fetched when result of previous fetch
# has been processed. Basically synchronous behavior
@gen.coroutine
def main_async_coroutine():
    print('Enter coroutine')
    for url in URLS:
        response = yield fetch_async_coro(url)
        print_size(response)
    print('Exit coroutine')
    return

# Fetches all urls in parallel
# Prints the results when all have responded
@gen.coroutine
def main_async_coroutine_2():
    print('Enter coroutine')
    responses = yield [fetch_async_coro(url) for url in URLS]
    for response in responses:
        print_size(response)
    print('Exit coroutine')
    return


# Uses ThreadPoolExecutor with blocking function
# .submit() returns a coroutine-compatible future
@gen.coroutine
def main_threaded_coro():
    print('Enter threaded')
    thread_pool = ThreadPoolExecutor(6)
    responses = yield [thread_pool.submit(sync_fetch, url) for url in URLS]
    for response in responses:
        print_size(response)
    print('Exit threaded')

def main_threaded_cb():
    print('Enter threaded')
    thread_pool = ThreadPoolExecutor(6)
    for url in URLS:
        future = thread_pool.submit(sync_fetch, url)
        future.add_done_callback(lambda f: print_size(f.result()))
    print('Exit threaded')


if __name__ == "__main__":
    loop = tornado.ioloop.IOLoop.current()
    # loop.run_sync(main_async)
    # loop.run_sync(main_async_coroutine_2)
    # loop.run_sync(main_threaded_coro)
    # loop.run_sync(main_threaded_cb)
    # loop.run_sync(periodic_cb)
    # main_async()
    # main_async_future()
    # main_threaded_cb()
    # loop.spawn_callback(periodic_cb)
    loop.start()

