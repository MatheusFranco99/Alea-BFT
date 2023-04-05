import socket
import sys
import threading
import signal

N = int(sys.argv[1])

cons = []

def clear_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind the socket to a specific address and port
    server_address = ('localhost', port)
    sock.bind(server_address)

    global cons
    cons += [sock]

    # listen for incoming connections
    sock.listen(3)

    # dictionary of persistent connections
    connections = {}

    while True:
        # wait for a connection
        print("Waiting for a connection...")
        conn, addr = sock.accept()
        cons += [conn]

        while True:
            data = conn.recv(1024)
            if not data:
                break
            else:
                print(f"Data received:{data}")
        sock.close()


for i in range(1,N+1):
    threading.Thread(target=clear_socket, args=(1350+i,)).start()


def signal_handler(sig, frame):
    print('Caught interrupt signal, closing connections...')
    close()

    # CLOSE NODE -> CLOSE CONNECTIONS (+ SERVER SOCKET)
def close():
    # Close the connections
    global cons
    for sock in cons:
        sock.close()

# CREATES SIGINT HANDLER -> TO CLOSE CONNECTIONS
signal.signal(signal.SIGINT, signal_handler)
