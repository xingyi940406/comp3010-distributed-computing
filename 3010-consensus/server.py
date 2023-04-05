import sys
import select
import json
import socket
import time
import random
import uuid

WELL_KNOWN_HOSTS = [
    'silicon.cs.umanitoba.ca',
    'eagle.cs.umanitoba.ca',
    'hawk.cs.umanitoba.ca',
    'osprey.cs.umanitoba.ca'
]


class Event:
    
    def __init__(self, id, name, expiry):
        self.id = id
        self.name = name
        self.expiry = expiry
        
    def renew(self, expiry):
        self.expiry = expiry

class Peer:
    
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name
        self.expiry = time.time() + 30 # TODO: 120
    
    def renew(self):
        self.expiry = time.time() + 30 # TODO: 120
        
    def info(self):
        print(self.host, self.port, self.name)

class Server:
    
    def __init__(self):
        self.gossipsReceived = []
        self.peers = {}
        
        for host in WELL_KNOWN_HOSTS:
            key = host + ':16000'
            self.peers[key] = Peer(host, 16000, 'WK')
        
        self.words = ['', '', '', '', '']
        self.events = {}
        e = Event(str(uuid.uuid4()), 'gossip', time.time() + 20) # TODO: 60
        self.events[e.id] = e
        
        self.host = None
        self.clientPort = None
        self.peerPort = None
    
    def createSockets(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.configSocket(clientSocket)
        self.configSocket(peerSocket)
        clientSocket.listen(5)
        self.setServerInfo(clientSocket, peerSocket)
        self.logSocketsInfo()
        return (clientSocket, peerSocket)
    
    def setServerInfo(self, clientSocket, peerSocket):
        self.host = socket.gethostname()
        self.clientPort = clientSocket.getsockname()[1]
        self.peerPort = peerSocket.getsockname()[1]
    
    def logSocketsInfo(self):
        print(f"Client | TCP | Port {self.clientPort} | Host {self.host}")
        print(f"Peer   | UDP | Port {self.peerPort} | Host {self.host}")
         
    def configSocket(self, s):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(False)
        s.bind(('', 0))
        
    def constructPeer(self, gossip):
        return Peer(gossip['host'], gossip['port'], gossip['name'])
    
    def getEventWithMinExpiry(self):
        return min(self.events.values(), key = lambda e: e.expiry)
    
    def clearExpiredPeers(self):
        keys = []
        for key, value in self.peers.items():
            if value.expiry < int(time.time()):
                keys.append(key)
        for key in keys:
            del self.peers[key]
            print(f'Cleared peer {key}')

    def start(self):
        clientSocket, peerSocket = self.createSockets()
        
        inputs = [clientSocket, peerSocket]
        clients = []
        outputs = []
        
        with clientSocket, peerSocket:
            while True:
                try:
                    event = self.getEventWithMinExpiry()
                    timeout = event.expiry - time.time()
                            
                    readable, writable, exceptional = select.select(
                        inputs + clients, 
                        outputs, 
                        inputs + clients, 
                        timeout if timeout > 0 else 1)
                    
                    print('Processing readable')
                    
                    for r in readable:
                        if r is peerSocket:
                            data, addr = r.recvfrom(1024)
                            res = json.loads(data.decode('utf-8', 'ignore'))
                            print(f"UDP message from {addr}: {res}")
                            command = res['command']
                            if command == 'GOSSIP':
                                self.onGossiped(int(peerSocket.getsockname()[1]), r, res)
                            elif command == 'GOSSIP_REPLY':
                                self.onGossipReplied(res)
                        elif r is clientSocket:
                            conn, addr = r.accept()
                            print('Connected from: ', addr)
                            conn.setblocking(False)
                            clients.append(conn)
                        elif r in clients:
                            data = r.recv(1024)
                            if not data or len(data) == 0:
                                clients.remove(r)
                            else:
                                req = json.loads(data.decode('utf-8', 'ignore'))
                                command = req['command']
                                print('Command:', command)
                                if command == 'SET':
                                    i = req['index']
                                    if i >= 0 and i < len(self.words):
                                        self.words[i] = req['value']
                                        reply = {
                                            'command': 'SET_REPLY',
                                            'words': self.words
                                        }
                                        r.sendall(json.dumps(reply).encode())
                        else:
                            print('Readable not found')
                            
                    print('Timed out')
                    
                    self.clearExpiredPeers()
                    
                    if event.name == 'gossip':
                        print('Gossiping to peers')
                        n = min(5, len(self.peers))
                        peers = random.sample(list(self.peers.values()), n)
                        for p in peers:
                            print(f'Gossiping to {p.host}:{p.port}')
                            gossip = {
                                "command": 'GOSSIP',
                                "host": self.host,
                                "port": self.peerPort,
                                "name": 'Me',
                                "messageID": str(uuid.uuid4())
                            }
                            peerSocket.sendto(json.dumps(gossip).encode(), (p.host, p.port))
                            #  ???
                        self.events[event.id].renew(time.time() + 10) # TODO: 60
                    elif event.name == 'consensus':
                        pass
                    
                except socket.timeout as e:
                    print('Time out')
                except KeyboardInterrupt as e:
                    sys.exit(0)
                except Exception as e:
                    print(e)

    def onGossipReplied(self, res):
        key = res['host'] + ':' + str(res['port'])
        peer = self.constructPeer(res)
        self.peers[key] = peer

    def onGossiped(self, port, peerSocket, res):
        gossipId = res['messageID']
        if gossipId not in self.gossipsReceived:
            self.gossipsReceived.append(gossipId)
            # TODO - debugging
            print(self.gossipsReceived)
            key = res['host'] + ':' + str(res['port'])
            if key not in self.peers:
                peer = self.constructPeer(res)
                self.peers[key] = peer
                          
                # TODO - debugging        
                for k, v in self.peers.items():
                    print(k)
                               
                reply = {
                    'command': 'GOSSIP_REPLY',
                    'host': socket.gethostname(),
                    'port': port,
                    'name': 'Me reply',
                }
                                        
                peerSocket.sendto(json.dumps(reply).encode(), (peer.host, peer.port))
            else:
                print(f'Renewing peer {key} expiry')
                self.peers[key].renew()
        else:
            print(f'Gossip {gossipId} exists')
            
def main():
    Server().start()

if __name__ == "__main__":
    main()