import json
import socket
import threading
import os

HOST = 'localhost'
PORT = 8080

def readToDos():
    try:
        with open('todos.json', 'r') as f:
            todos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        todos = []
    return todos

def writeToDos(todos):
    with open('todos.json', 'w') as f:
        json.dump(todos, f)

def runWebServer(client_socket, todo_list):
    request = client_socket.recv(1024).decode()
    method, path, version = request.split('\n')[0].split()

    if method == 'GET':
        if path == '/todos':
                        
            with open('index.html', 'r') as f:
                main = f.read()

            todoUI = ''
            for todo in todo_list:
                todoUI += f'<li>{todo["task"]}<br><img src="{todo["image"]}"></li>'
            todosUI = f'<ul>{todoUI}</ul>'
            main = main.replace('{TODO_LIST}', todosUI)

            # Set the CORS policy headers
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Type': 'text/html',
                'Content-Length': str(len(main))
            }

            # Send the response with headers
            result = f'HTTP/1.1 200 OK\r\n'
            for key, value in headers.items():
                result += f'{key}: {value}\r\n'
            result += '\r\n'
            result += main
            client_socket.send(result.encode())

        else:
            # Send a 404 response if the path is not recognized
            result = 'HTTP/1.1 404 Not Found\r\n\r\n'
            client_socket.send(result.encode())
    
    elif method == 'POST':
        if path == '/login':
            print('Logging in...')
            print('Request for logging')
            print(request)
            body = request.split('\r\n\r\n')[1]
            username = None
            password = None
            for field in body.split('&'):
                name, value = field.split('=')
                if name == 'username':
                    username = value
                elif name == 'password':
                    password = value
                    
            print('Name', username)
            print('PSW', password)

            if username == 'xrm' and password == '123':
                print('Matched')
                
                result = f'''HTTP/1.1 200 OK
                Content-Type: text/html
                Set-Cookie: username={username}
                
                
                '''
                
                print(result)
                
                client_socket.send(result.encode())
            
            else:
                pass
                # response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
                # response += LOGIN_PAGE.replace('<form', '<p style="color: red">Invalid username or password</p><form')
                # client_socket.send(response.encode())
        elif path == '/todos':
            pass
    elif method == 'DELETE':
        pass
    else:
        result = 'HTTP/1.1 405 Method Not Allowed\r\n\r\n'
        client_socket.send(result.encode())

    client_socket.close()

if __name__ == '__main__':
    todos = readToDos()

    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sk.bind((HOST, PORT))
    sk.listen()
    print(f'Server listening on {HOST}:{PORT}')
    print('http://localhost:8080/todos')
    
    while True:
        conn, addr = sk.accept()
        print(f'Connected to {addr}')
        t = threading.Thread(target=runWebServer, args=(conn,todos))
        t.start()
        writeToDos(todos)
