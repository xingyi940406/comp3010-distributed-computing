import socket
import time
import sys
from contants import Decoding, Port

class Monitor:
    def __init__(
        self, 
        clientPort = Port.CLIENT, 
        host = Port.HOST
    ):
        self.clientPort = clientPort
        self.host = host
        
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
            self.connectOrRetry(clientSocket)
            while True:
                id = input('\nCheck status for job with ID: ')
                try:
                    req = f'STATUS {int(id)}'
                    clientSocket.send(req.encode())
                    data = clientSocket.recv(1024)
                    if data:
                        print(data.decode(Decoding.UTF_8))
                except socket.error:
                    clientSocket = socket.socket()
                    self.connectOrRetry(clientSocket)
                except ValueError:
                    print("\nEnter job ID again as an integer")
    
    def connectOrRetry(self, clientSocket):
        connected = False
        while not connected:
            try:
                print('Trying to connect...')
                clientSocket.connect((self.host, self.clientPort))
                print('Connected')
                connected = True
            except socket.error:
                print('Reconnect after 1 sec')
                time.sleep(1)

def main():
    args = sys.argv
    n = len(args)
    if n == 3:
        Monitor(int(args[1]), args[2]).run()
    elif n == 2:
        Monitor(int(args[1])).run()
    else:
        Monitor().run()

if __name__ == "__main__":
    main()