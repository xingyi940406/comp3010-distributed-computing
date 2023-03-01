import json
import socket
import threading
import os

HOST = 'localhost'
PORT = 8080

def handle_request(client_socket):
    request = client_socket.recv(1024).decode()
    method, path, version = request.split('\n')[0].split()
    
    if method == 'GET':
        if path == '/todos':
            # Render the list of todos as JSON
            todo_list = [{'id': 1, 'task': 'todo1', 'completed': False, 'image': 'https://via.placeholder.com/150'},
                         {'id': 2, 'task': 'todo2', 'completed': True, 'image': 'https://via.placeholder.com/150'},
                         {'id': 3, 'task': 'todo3', 'completed': False, 'image': 'https://via.placeholder.com/150'}]
            
            # Convert the list to JSON and add it to the HTML template
            todo_html = ''
            for todo in todo_list:
                todo_html += f'<li>{todo["task"]}<br><img src="{todo["image"]}"></li>'
                
            html_content = f'<html><body><h1>Todo List</h1><ul>{todo_html}</ul></body></html>'
            
            # Send the response
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html_content)}\r\n\r\n{html_content}'
            client_socket.send(response.encode())
            
        else:
            # Send a 404 response if the path is not recognized
            response = 'HTTP/1.1 404 Not Found\r\n\r\n'
            client_socket.send(response.encode())
    else:
        # Send a 405 response if the method is not GET
        response = 'HTTP/1.1 405 Method Not Allowed\r\n\r\n'
        client_socket.send(response.encode())
    
    client_socket.close()

    
def start_server():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Set the socket options and bind to the host and port
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    
    # Listen for incoming connections
    server_socket.listen()
    print(f'Server listening on {HOST}:{PORT}')
    print('http://localhost:8080/todos')
    
    while True:
        # Accept a new client connection
        client_socket, client_address = server_socket.accept()
        print(f'Client connected from {client_address}')
        
        # Start a new thread to handle the client request
        client_thread = threading.Thread(target=handle_request, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    start_server()
