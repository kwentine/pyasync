from socket import socket

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


def main_sync(hosts, callback):
    for host in hosts:
        response = fetch_sync(host)
        callback(host, response)
