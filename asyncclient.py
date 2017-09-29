import selectors
import socket
from datetime import datetime

selector = selectors.DefaultSelector()

class AsyncHTTPClient:

    def __init__(self, host, callback, path='/'):
        self.host = host
        self.path = path
        self.callback = callback

        self.request = '\r\n'.join([
            'GET {} HTTP/1.1'.format(path),
            'Host: {}'.format(host),
            'Connection: close',
            '\r\n'
        ])
        
        self.response = b''
        self.counter = 0
        self.done = False

    def fetch(self):
        
        self.sock = socket.socket()
        self.sock.setblocking(False)

        try:
            self.sock.connect((self.host, 80))
        except BlockingIOError:
            pass
        
        selector.register(self.sock, selectors.EVENT_WRITE, data=self.send_request)
        return self

    def send_request(self):
        print('Connected to {}'.format(self.host))
        self.sock.send(self.request.encode('ascii'))
        selector.modify(self.sock, selectors.EVENT_READ, data=self.receive_data)
        
    def receive_data(self):
        chunk = self.sock.recv(4096)

        if not chunk:
            selector.unregister(self.sock)
            self.callback(self.host, self.response)
            self.done = True
        else:
            self.counter += 1
            print('({}) Chunk {}: {} kb'.format(self.host, self.counter, len(chunk)))
            self.response += chunk

def fetch_sync(hostname, path='/'):

    address = (hostname, 80)
    sock = socket.socket()
    sock.connect(address) # Blocking

    lines = [
        'GET {} HTTP/1.1'.format(path),
        'Host: {}'.format(hostname),
        'Connection: close', # close the connection immediatly when the response is finished
        '\r\n'
    ]

    request = '\r\n'.join(lines)
    bytes_to_send = request.encode('ascii') # Convert string to sequence of bytes

    sock.send(bytes_to_send) 

    response = b''
    chunk = sock.recv(4096)
    while chunk:
        response += chunk
        chunk = sock.recv(4096) # Blocking. Returns 0 when the connection closes.

    return response


def timed(func):
    def wrapped(*args, **kwargs):
        start = datetime.now()
        print("* Enter %s" % func.__name__)
        func(*args, **kwargs)
        end = datetime.now()
        dt = end - start
        name = func.__name__
        print("* %s ran in %s" % (name, dt))
    return wrapped

@timed
def main_async(hosts, callback):            

    clients = [AsyncHTTPClient(host, callback).fetch() for host in hosts]

    while not all(map(lambda client: client.done, clients)):
        events = selector.select()
        for key, evts in events:  
            callback = key.data
            callback()

@timed    
def main_sync(hosts, callback):
    for host in hosts:
        response = fetch_sync(host)
        callback(host, response)
            
if __name__ == "__main__":

    callback = lambda host, response: print(' - {} : {} KB'.format(host, len(response)))
    
    hosts = [
        'www.lepoint.fr',
    ]

    main_sync(hosts, callback)
    main_async(hosts, callback)

