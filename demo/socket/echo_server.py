#!/usr/bin/python3

# started with https://docs.python.org/3/library/socket.html#example

# chat-hopper!
# Give the message to the next person


import socket
import sys

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port

lastWord = "F1rst p0st"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # blocking, but default
    # https://docs.python.org/3/library/socket.html#notes-on-socket-timeouts
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # overall timeout
    #s.settimeout(5)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        try:
            conn, addr = s.accept()
            # I can set a timeout here, for the client socket, too.
            conn.settimeout(5)
            with conn:
                print('Connected by', addr)
                data = conn.recv(1024)
                print(data)
                if data:
                    print('swapping')
                    currWord = lastWord
                    lastWord = data.strip()
                conn.sendall(currWord)
                conn.sendall(b'Bye!')
                conn.close()
        except socket.timeout as e:
            #print('timeout')
            pass
        except KeyboardInterrupt as e:
            print("RIP")
            sys.exit(0)
        except Exception as e:
            print("Something happened... I guess...")
            print(e)

