from fib import fib
from fibservsync import handle_client
from threading import Thread
import socket

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
