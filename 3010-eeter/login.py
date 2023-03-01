import socket
import threading

# Define the server address and port
SERVER_ADDRESS = ('localhost', 8000)

# Define the HTML response for the login page
LOGIN_PAGE = '''<!DOCTYPE html>
<html>
<head>
    <title>Login Page</title>
</head>
<body>
    <h1>Login Page</h1>
    <form method="POST" action="/login">
        <label for="username">Username:</label>
        <input type="text" name="username" id="username" required>
        <br>
        <label for="password">Password:</label>
        <input type="password" name="password" id="password" required>
        <br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
'''

# Define the HTML response for the logged in page
LOGGED_IN_PAGE = '''<!DOCTYPE html>
<html>
<head>
    <title>Logged In Page</title>
</head>
<body>
    <h1>Logged In Page</h1>
    <p>Welcome, {username}!</p>
</body>
</html>
'''

# Define a function to handle each client connection
def handle_client_connection(client_socket):
    # Receive the client request
    request = client_socket.recv(1024).decode()

    # Extract the request method and path
    request_method = request.split(' ')[0]
    path = request.split(' ')[1]

    # Send the appropriate response
    if request_method == 'GET' and path == '/':
        response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + LOGIN_PAGE
        client_socket.send(response.encode())
    elif request_method == 'POST' and path == '/login':
        # Extract the login form data
        form_data = request.split('\r\n')[-1]
        username = form_data.split('&')[0].split('=')[1]
        password = form_data.split('&')[1].split('=')[1]

        # Check if the username and password are valid
        if username == 'admin' and password == 'password':
            # Set the cookie and send the logged in page
            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
            response += 'Set-Cookie: username={}\r\n'.format(username)
            response += '\r\n' + LOGGED_IN_PAGE.format(username=username)
            client_socket.send(response.encode())
            
            # Display tweets after login
            
        else:
            # Send the login page with an error message
            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
            response += LOGIN_PAGE.replace('<form', '<p style="color: red">Invalid username or password</p><form')
            client_socket.send(response.encode())

    # Close the client socket
    client_socket.close()

# Create a socket object and bind it to the server address and port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDRESS)

# Listen for incoming connections
server_socket.listen(5)
print('Server listening on {}:{}'.format(*SERVER_ADDRESS))

# Handle incoming connections in a loop
while True:
    # Accept the client connection and create a new thread to handle it
    client_socket, client_address = server_socket.accept()
    print('Accepted connection from {}:{}'.format(*client_address))
    client_thread = threading.Thread(target=handle_client_connection, args=(client_socket,))
    client_thread.start()
