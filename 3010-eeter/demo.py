import os
import threading
import socket

def handle_client(client_socket, client_address):
    # Receive client request
    request = client_socket.recv(1024).decode()
    # Extract requested file path from HTTP request
    path = request.split()[1]
    # If path is root (/), serve index.html
    if path == '/':
        path = '/index.html'
    # Construct full file path by joining with current working directory
    file_path = os.path.join(os.getcwd(), path.lstrip('/'))
    print(file_path)
    # Check if file exists and is an HTML file
    if os.path.isfile(file_path) and file_path.endswith('.html'):
        # Send HTTP response with 200 OK status code and file contents
        with open(file_path, 'rb') as f:
            file_contents = f.read()
            response = ('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n'.format(len(file_contents)) + file_contents).encode
            client_socket.sendall(response)
    else:
        # Send HTTP response with 404 Not Found status code and error message
        response = ('HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<html><body><h1>404 Not Found</h1><p>The requested URL {} was not found on this server.</p></body></html>'.format(path)).encode()
        client_socket.sendall(response)
    # Close client socket
    client_socket.close()

def main():
    # Create socket and bind to localhost:8000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8000))
    server_socket.listen(5)
    print('Server listening on localhost:8000...')
    # Accept client connections and spawn thread to handle each request
    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection from {}'.format(client_address))
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == '__main__':
    main()
