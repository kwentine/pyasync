from fib import fib
import socket

def run_server(host='127.0.0.1', port=5000):

    # Create a TCP socket and listen for incoming connexions
    s = socket.socket() 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    print("Fibonacci server on port %d ..." % port)
    
    while True:
        # Wait for incoming connexion
        # Blocks program execution
        conn, addr = s.accept()
        with conn: 
            handle_client(conn) 


def handle_client(conn):
    """Receive integer from client and send back corresponding Fibonacci number"""
    while True:
        try:
            # Wait for data from the client
            # Blocking call
            data = conn.recv(256) 
            n = int(data.decode('ascii'))
            result = fib(n)
            response = str(result).encode('ascii') + b'\n'
            conn.send(response)
        except:
            break
    
    # Close connection
    print('Client disconnected')
    conn.close()


if __name__ == "__main__":
    run_server()
