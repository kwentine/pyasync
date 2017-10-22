import selectors
import socket
from datetime import datetime

selector = selectors.DefaultSelector()

class AsyncHTTPClient:
    """Callback based asynchronous HTTP client.
    
    Uses non blocking sockets, and must be driven by an event loop
    that polls a selector.

    """
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

@timed
def main_async(hosts, callback):            

    clients = [AsyncHTTPClient(host, callback).fetch() for host in hosts]

    while not all(map(lambda client: client.done, clients)):
        events = selector.select()
        for key, evts in events:  
            callback = key.data
            callback()
            
if __name__ == "__main__":

    callback = lambda host, response: print(' - {} : {} KB'.format(host, len(response)))
    
    hosts = [
        'www.lepoint.fr',
    ]

    main_async(hosts, callback)

