import socket
import sys
import select

class Job:   
    
    def __init__(self, key: int, payload: str):
        self.key = key;
        self.payload = payload
        self.issued = False
        self.completed = False
        
        
class Broker:
    
    def __init__(self, host: str, clientPort: int, workerPort: int):
        self.jobs = []
        self.host = host
        self.clientPort = clientPort
        self.workerPort = workerPort
        
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as left, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as right:
            self.initSocket(left, self.host, self.clientPort)
            self.initSocket(right, self.host, self.workerPort)
            
            inputs = [left, right]
            clients = []
            workers = []
            outputs = []
            while True:
                try:
                    readable, writeable, exceptional = select.select(
                        inputs + clients + workers, 
                        outputs, 
                        inputs + clients + workers, 
                        5)
                    
                    print('Released')
                    
                    for r in readable:
                        if r is left:
                            conn, addr = left.accept()
                            
                            print('Client', addr)
                            
                            conn.setblocking(False)
                            clients.append(conn)
                        elif r is right:
                            conn, addr = right.accept()
                            
                            print('Worker', addr)
                            
                            conn.setblocking(False)
                            workers.append(conn)
                        elif r in clients:
                            data = r.recv(1024)
                            
                            print("Client Data", data)
                            print("Client Str", data.decode('utf-8'))

                            if len(data) == 0:
                                clients.remove(r)
                                
                                print('Clients size', len(clients))
                                
                            elif data:
                                req = data.decode('utf-8')
                                payload = req.split('JOB ')[1]
                                
                                # TODO - check for empty payload
                                
                                print('Adding job', payload)
                                self.addJob(Job(self.size(), payload))
                        elif r in workers:
                            data = r.recv(1024)
                            
                            print("Worker Data", data)
                            print("Worker Str", data.decode('utf-8'))
                            
                            if len(data) == 0:
                                workers.remove(r)
                                
                                print('Workers size', len(workers))
                                
                            elif data:
                                req = data.decode('utf-8').split(' ')
                                
                                if len(req) == 0:
                                    
                                    print('Shit')
                                    
                                else:
                                    if req[0] == 'GET':
                                        print('Worker - GET', req[0])
                                        print('Searching for job')
                                        
                                        res = ''
                                        for j in self.jobs:
                                            if (j.issued == False):
                                                res = j.payload
                                                j.issued = True
                                        
                                        if (res == ''):
                                            print('-- Fuck --')
                                            # Not found
                                        else:
                                            r.sendall(res.encode())
                                            print('Job sent')
                                    elif req[0] == 'POST':
                                        print('Worker - POST')
                                        print(req[1])
                                    else:
                                        print('Worker - SHIT')
                        else:
                            print('WAT')
                            
                except socket.timeout as e:
                    pass
                except KeyboardInterrupt as e:
                    print("RIP")
                    sys.exit(0)
                except Exception as e:
                    print("Something happened... I guess...")
                    print(e)

    def initSocket(self, s, host, port):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.setblocking(False)
        s.listen()
    
    def addJob(self, job: Job):
        self.jobs.append(job)
        
    def job(self, key: int):
        return self.jobs[key] if self.verifyKey(key) else None

    def size(self):
        return len(self.jobs)
    
    def verifyKey(self, id):
        return id >= 0 and id < self.size()
    
    def printJobs(self):
        for job in self.jobs:
            print(job.key, job.payload)
        
Broker('localhost', 3000, 3001).run()
