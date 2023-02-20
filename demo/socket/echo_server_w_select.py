#!/usr/bin/python3

# started with https://docs.python.org/3/library/socket.html#example

# chat-hopper!
# Give the message to the next person


import socket
import sys
import select

HOST = 'localhost'                 # Symbolic name meaning all available interfaces
PORT = 10000             # Arbitrary non-privileged port

lastWord = "F1rst p0st"

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# blocking, but default
# https://docs.python.org/3/library/socket.html#notes-on-socket-timeouts
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# overall timeout
#s.settimeout(5)
serverSocket.bind((HOST, PORT))
serverSocket.listen()
myReadables = [serverSocket, ] # not transient
myWriteables = []

myClients = [] # are transient
while True:
    try:
        readable, writeable, exceptions = select.select(
            myReadables + myClients,
            myWriteables,
            myReadables,
            5
        )
        print('released from block')
        for eachSocket in readable:
            if eachSocket is serverSocket:
                # new client

                conn, addr = serverSocket.accept()
                print('Connected by', addr)
                myClients.append(conn)
                #... read handled by select, and ... later
            elif eachSocket in myClients:
                # read, 
                data = eachSocket.recv(1024)
                datastr = data.decode('utf-8') # be a string
                print(data)
                if data:
                    print('swapping')
                    currWord = lastWord
                    lastWord = data.strip()
                    eachSocket.sendall(currWord.encode())
                    clean  = datastr.strip()
                    if clean == "" or clean == "exit":
                        eachSocket.close()
                        myClients.remove(eachSocket)
                else:
                    # close this client....
                    # they are closing on us!
                    print("Removing client")
                    myClients.remove(eachSocket)
        for problem in exceptions:
            # ... probably a client socket
            print("has problem")
            if problem in myClients:
                myClients.remove(problem)


            
    except socket.timeout as e:
        #print('timeout')
        pass
    except KeyboardInterrupt as e:
        print("RIP")
        sys.exit(0)
    except Exception as e:
        print("Something happened... I guess...")
        print(e)

