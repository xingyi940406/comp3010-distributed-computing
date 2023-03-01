import socket
import threading
import os

def handle_client(conn, addr):
    with conn:
        data = conn.recv(1024)
        request = data.decode()
        method, path, version = request.split('\r\n')[0].split(' ')
        if method != 'GET':
            conn.sendall(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')
            return
        if path == '/':
            path = '/login.html'
        file_path = os.path.join('', path[1:])
        if not os.path.isfile(file_path):
            conn.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')
            return
        with open(file_path, 'rb') as file:
            content = file.read()
        conn.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
        conn.sendall(content)

def start_server():
    host = 'localhost'
    port = 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        print(f'Server running on http://{host}:{port}')
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == '__main__':
    start_server()
