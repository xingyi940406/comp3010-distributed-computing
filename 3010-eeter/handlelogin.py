import socket

HOST = 'localhost'
PORT = 8080

def handle_request(client_socket):
    request = client_socket.recv(1024).decode()
    method, path, http_version = request.split(' ')
    headers, body = request.split('\r\n\r\n', 1)
    
    if method == 'POST' and path == '/login':
        username, password = body.split('&')
        # Here you would validate the username and password against a database or some other data source
        # If the username and password are valid, set a cookie in the response headers
        response_headers = [
            'HTTP/1.1 200 OK',
            'Content-Type: text/plain',
            'Set-Cookie: username={}'.format(username.split('=')[1]), # Set the username cookie
            'Set-Cookie: logged_in=true', # Set the logged_in cookie
            'Connection: close',
            ''
        ]
        response_body = 'Logged in successfully'
    else:
        response_headers = [
            'HTTP/1.1 404 Not Found',
            'Content-Type: text/plain',
            'Connection: close',
            ''
        ]
        response_body = '404 Not Found'

    response = '\r\n'.join(response_headers) + '\r\n' + response_body
    client_socket.send(response.encode())
    client_socket.close()

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f'Server running on {HOST}:{PORT}')
        while True:
            client_socket, client_address = server_socket.accept()
            print(f'Client connected from {client_address[0]}:{client_address[1]}')
            handle_request(client_socket)

if __name__ == '__main__':
    run_server()
