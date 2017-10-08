# Basic UDP server application
from time import sleep
from threading import Thread
import socket


def fib(n):
    """Compute nth Fibonacci number"""
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)

def handle_client(conn):
    """Receive integer from client and send back its square"""
    with conn:
        while True:
            data = conn.recv(256) # Blocking
            try:
                n = int(data.decode('ascii'))
            except ValueError:
                break
            res = str(fib(n)) + '\n'
            conn.send(res.encode('ascii'))

def run_server(host='127.0.0.1', port=5000):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server on port %d ..." % port)
    while True:
        conn, addr = s.accept() # Blocking
        print('Connection from {}.'.format(addr))
        Thread(target=handle_client, args=(conn,)).start() 

if __name__ == "__main__":
    run_server()
