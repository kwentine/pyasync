import selectors
import socket

selector = selectors.DefaultSelector()

host = 'www.dabeaz.com'
path = '/'
addr = (host, 80)
response = b''

sock = socket.socket()
sock.setblocking(False)


def on_connect(sock):
    print('Connected.')
    request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(path, host)
    sock.send(request.encode('ascii'))
    selector.modify(sock, selectors.EVENT_READ, data=on_data)

def on_data(sock):
    global done, response
    
    chunk = sock.recv(4096)
    print('Received chunk of size {}'.format(len(chunk)))
    response += chunk
    if not chunk:
        done = True
        selector.unregister(sock)
        on_finish()

def on_finish():
    print('Response size: {}'.format(len(response)))
    
try:
    sock.connect(addr)
except BlockingIOError:
    pass

selector.register(
    sock, # File object
    selectors.EVENT_WRITE, # We want to know when the socket is ready for writing
    data=on_connect
)

done = False
while not done: 
    events = selector.select() # Blocks until something is ready
    for key, evts in events:   # returns a list of (key, events) tuple
        callback = key.data
        callback(key.fileobj)
