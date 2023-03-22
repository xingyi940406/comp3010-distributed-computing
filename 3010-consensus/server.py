import sys
import socket
import select

from utils import extractCommand

class Server:
    def __init__(self, port, host = 'localhost'):
        self.port = port
        self.host = host
        
    def start(self):
        print(self.host + ':' + str(self.port))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peerSocket:
            peerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            peerSocket.bind((self.host, self.port))
            peerSocket.setblocking(False)
            peerSocket.listen()

            inputs = [peerSocket]
            clients = []
            outputs = []
            
            while True:
                try:
                    readable, writable, exceptional = select.select(inputs + clients, outputs, inputs + clients, 3)
                    for r in readable:
                        if r is peerSocket:
                            conn, addr = r.accept()
                            conn.setblocking(False)
                            clients.append(conn)
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
    args = sys.argv
    
    if len(args) == 3:
        port = int(args[1])
        host = args[2]
        Server(port, host).start()
    elif len(args) == 2:
        port = int(args[1])
        Server(port).start()
    else:
        print('Invalid args')

if __name__ == "__main__":
    main()