import sys
import socket
import select

from utils import extractCommand

class Server:
    
    def createSockets(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.configSocket(clientSocket)
        self.configSocket(peerSocket)
        clientSocket.listen(5)
        self.logSocketsInfo(clientSocket, peerSocket)
        return (clientSocket, peerSocket)
    
    def logSocketsInfo(self, clientSocket, peerSocket):
        clientPort = clientSocket.getsockname()[1]
        peerPort = peerSocket.getsockname()[1]
        host = socket.gethostname()
        print(f"Client | TCP | Port {clientPort} | Host {host}")
        print(f"Peer   | UDP | Port {peerPort} | Host {host}")
         
    def configSocket(self, s):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(False)
        s.bind(('', 0))
        
    def start(self):
        clientSocket, peerSocket = self.createSockets()
        
        inputs = [clientSocket, peerSocket]
        clients = []
        outputs = []
        
        with clientSocket, peerSocket:
            while True:
                try:
                    readable, writable, exceptional = select.select(
                        inputs + clients, 
                        outputs, 
                        inputs + clients, 
                        3)
                    
                    for r in readable:
                        if r is clientSocket:
                            conn, addr = r.accept()
                            print('Connected from: ', addr)
                            conn.setblocking(False)
                            clients.append(conn)
                        elif r is peerSocket:
                            data, addr = r.recvfrom(1024)
                            print(f"UDP message from {addr}: {data.decode()}")
                        elif r in clients:
                            request = r.recv(1024)
                            if not request or len(request) == 0:
                                clients.remove(r)
                            else:
                                data = request.decode('utf-8', 'ignore')
                                command = extractCommand(data)
                                print('Command:', command)
                                response = 'Received command: ' + data
                                r.sendall(response.encode())
                        else:
                            print('Readable not found')   
                except socket.timeout as e:
                    print('Time out')
                except KeyboardInterrupt as e:
                    sys.exit(0)
                except Exception as e:
                    print(e)

def main():
    Server().start()

if __name__ == "__main__":
    main()