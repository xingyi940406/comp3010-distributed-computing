import os
import threading
import socket

def handle_request(client_socket, client_address):
    request = client_socket.recv(1024)
    filename = get_filename(request)
    if os.path.isfile(filename):
        response = generate_response(filename)
    else:
        response = b'HTTP/1.1 404 Not Found\r\n\r\n'
    client_socket.sendall(response)
    client_socket.close()

def get_filename(request):
    request_str = request.decode()
    parts = request_str.split()
    filename = parts[1].lstrip('/')
    if filename == '':
        filename = 'index.html'
    return filename

def generate_response(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    response = b'HTTP/1.1 200 OK\r\n'
    response += b'Content-Type: text/html\r\n'
    response += b'Content-Length: {}\r\n'.format(len(content))
    response += b'Connection: close\r\n'
    response += b'\r\n'
    response += content
    return response

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen()
    while True:
        client_socket, client_address = server_socket.accept()
        t = threading.Thread(target=handle_request, args=(client_socket, client_address))
        t.start()

if __name__ == '__main__':
    start_server()
