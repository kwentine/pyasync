# Using a socket to connect to HTTPS server
import socket, ssl

address = host, port = ('www.python.org', 443)

context = ssl.create_default_context()
sock = context.wrap_socket(socket.socket(), server_hostname=host)

sock.connect(address)
print('Connected.')

n = sock.sendall(b'HEAD / HTTP/1.1\r\nHost: www.python.org\r\n\r\n')
print('Request sent', n)

# Collect the response by chunks
response = b''

chunk = sock.recv(1024)
print(chunk.decode('utf8'))

while chunk:
    response += chunk
    chunk = sock.recv(1024) # This blocks if all data has been received...
    print(len(chunk))
    
print(response.decode('utf8'))
