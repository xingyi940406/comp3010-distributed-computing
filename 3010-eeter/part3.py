import socket

# Connect to the other Python socket server
server_ip = 'localhost'
server_port = 3000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

# Add a post
post = "This is a sample post."
request = "POST " + post
client_socket.send(request.encode())
post_id = client_socket.recv(1024).decode()

# Send a POST request to the API endpoint with the cookie and Access-Control-Allow-Origin header
url = "/api/tweet"
data = f'{{"id": "{post_id}", "text": "{post}"}}'
headers = {"Cookie": "user=david", "Access-Control-Allow-Origin": "*"}
request_string = f"POST {url} HTTP/1.1\r\nHost: localhost:3000\r\n"
request_string += "\r\n".join([f"{key}: {value}" for key, value in headers.items()])
request_string += f"\r\nContent-Length: {len(data)}\r\n\r\n{data}"
client_socket.send(request_string.encode())

# Delete the post if the response was successful
response = client_socket.recv(1024).decode()
if "HTTP/1.1 200 OK" in response:
    delete_request = "DELETE " + post_id
    client_socket.send(delete_request.encode())

# Close the socket connection
client_socket.close()
