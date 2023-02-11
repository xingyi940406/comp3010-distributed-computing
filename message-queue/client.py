import socket
import time

requests = []

for i in range(3):
    requests.append('JOB job-' + str(i))

clients = [
    socket.socket(socket.AF_INET, socket.SOCK_STREAM),
    socket.socket(socket.AF_INET, socket.SOCK_STREAM),
    socket.socket(socket.AF_INET, socket.SOCK_STREAM)
]

for client in clients:
    client.connect(('localhost', 10000))

for request in requests:
    for i, client in enumerate(clients):
        time.sleep(2)
        o = request + '-client-' + str(i)
        client.send(o.encode())

for client in clients:
    client.close()