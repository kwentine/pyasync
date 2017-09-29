# Using a socket to connect to HTTPS server
import socket

address = host, port = ('www.dabeaz.com', 80)
path = '/'

sock = socket.socket()

sock.connect(address)
print('Connected.')

request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: keep-alive\r\n\r\n'.format(path, host)
bytes_to_send = request.encode('ascii')
print('Bytes to send: {}'.format(len(bytes_to_send)))
bytes_sent = sock.send(bytes_to_send)
print('Bytes sent: {}'.format(bytes_sent))

# Collect the response by chunks
response = b''

chunk = sock.recv(1024)
print('First bytes received')
while chunk:
    response += chunk
    chunk = sock.recv(1024) # This blocks if all data has been received...
    
print(response.decode('utf8'))
sock.close()
