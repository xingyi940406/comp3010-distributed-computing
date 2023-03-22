import sys
import socket

class Client:
    def __init__(self, targetPort, targetHost = 'localhost'):
        self.targetPort = targetPort
        self.targetHost = targetHost
    
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
            try:
                clientSocket.connect((self.targetHost, self.targetPort))
                
                while True:
                    request = input('Command: ')
                    clientSocket.send(request.encode())
                    response = clientSocket.recv(1024)
                    if response:
                        data = response.decode('utf-8', 'ignore')
                        print(data)
            except socket.error:
                print('Socket error')
                
def main():
    args = sys.argv
    
    if len(args) == 3:
        port = int(args[1])
        host = args[2]
        Client(port, host).start()
    elif len(args) == 2:
        port = int(args[1])
        Client(port).start()
    else:
        print('Invalid args')

if __name__ == "__main__":
    main()