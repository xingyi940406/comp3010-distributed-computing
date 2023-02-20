# Echo client program
import socket
import json
import time

HOST = 'wren.cs.umanitoba.ca'    # The remote host
PORT = 8008 # The same port as used by the server

count = 1
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        asStr = "{}, ah ha ha".format(count)
        count += 1
        asBytes = asStr.encode()

        s.sendall(asBytes)
        data = s.recv(1024)
    print('Received', repr(data))
    time.sleep(1)
