# Fetch HTTP url and return response
import socket
import sys
import re


def fetch(hostname, path='/'):

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

def get_content_length(hostname, path='/'):
    
    address = (hostname, 80)
    sock = socket.socket()
    sock.connect(address) # Blocking
    # print('Connected to {}'.format(hostname))

    request = 'HEAD {} HTTP/1.1\r\nHost: {}\r\n\r\n'.format(path, hostname)

    bytes_to_send = request.encode('ascii') # Convert string to sequence of bytes
    sock.send(bytes_to_send)

    response = sock.recv(1024) # Blocking
    text = response.decode('utf8')

    try:
        content_length = re.search(r'Content-Length:\s*(\d+)', text).group(1)
    except:
        return 0

    return int(content_length)

if __name__ == "__main__":

    hosts = [
        'www.lemonde.fr',
        'www.liberation.fr',
        'www.bfmtv.com',
        'www.leprogres.fr'
    ]
    
    for host in hosts:
        response = fetch(host)
        print('{}: {} bytes'.format(host, len(response)))

