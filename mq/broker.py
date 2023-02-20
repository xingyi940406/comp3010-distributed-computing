import socket
import sys
import select
import time

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
                        
                            if len(data) == 0:
                                clients.remove(r)
                                
                                print('Clients size after removal', len(clients))
                                
                            elif data:
                                for payload in data.decode('utf-8').split('JOB '):
                                    # TODO - check for empty payload
                                    
                                    print('Adding job', payload)
                                
                                    self.addJob(Job(self.size(), payload))
                                    
                                    print('Queue size after ADD', len(self.jobs))
                                
                        elif r in workers:
                            data = r.recv(1024)
                            
                            print("Worker Data", data)
                                                        
                            if len(data) == 0:
                                
                                workers.remove(r)
                                print('Worker removed')
                                print('Workers size', len(workers))
                                
                            elif data:
                                decoded = data.decode('utf-8').split(' ')
                                
                                if len(decoded) == 0:
                                    
                                    print('Shit')
                                    
                                else:
                                    if decoded[0] == 'GET':
                                        print('Worker - GET', decoded[0])
                                        print('Searching for job')
                                        
                                        target = None
                                        found = False
                                        i = 0
                                        while (i < len(self.jobs) and found == False):
                                            job = self.jobs[i]
                                            if (job.issued == False):
                                                job.issued = True
                                                target = job
                                                found = True
                                            i += 1
                                            
                                        if (found == False):
                                            print('-- Job not found --')
                                        else:
                                            r.sendall(target.payload.encode()) # Send job
                                            
                                            print('Job sent', i)
                                            print('Workers size', len(workers))
                                            
                                    elif decoded[0] == 'POST':
                                        print('Worker - POST')
                                        print(decoded[1])
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
        print('Job added - ', job.payload)
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
        
Broker('localhost', 8000, 8001).run()
