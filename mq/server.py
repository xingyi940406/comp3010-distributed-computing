import socket
import select
import sys
from contants import Delimiter, Status, Event, Connection, Decoding
    
class Broker:
    class Job:   
        def __init__(self, id, work):
            self.id = id;
            self.work = work
            self.status = Status.PENDING
            
        def toString(self):
            return self.id + Delimiter.SPACE + self.work
        
    def __init__(
        self, 
        clientPort = Connection.CLIENT_PORT, 
        workerPort = Connection.WORKER_PORT, 
        host = Connection.HOST
    ): 
        self.clientPort = clientPort
        self.workerPort = workerPort
        self.host = host
        self.queue = []
        
    def run(self):
        print('Client port:', self.clientPort, ' | ', 'Worker port:', self.workerPort)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as workerSocket:
            self.openSocket(clientSocket, self.clientPort)
            self.openSocket(workerSocket, self.workerPort)
            self.listen(clientSocket, workerSocket)
        
    def openSocket(self, sk, port):
        sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sk.bind((self.host, port))
        sk.setblocking(False)
        sk.listen()
            
    def listen(self, clientSocket, workerSocket):
        inputs = [clientSocket, workerSocket]
        clients = []
        workers = []
        outputs = []
        
        while True:
            try:
                readable = select.select(inputs + clients + workers, outputs, inputs + clients + workers, 3)
                for r in readable:
                    if r is clientSocket:
                        self.readOn(r, clients)
                    elif r is workerSocket:
                        self.readOn(r, workers)
                    elif r in clients:
                        self.onClientObserved(r, clients)
                    elif r in workers:
                        self.onWorkerObserved(r, workers)
                    else:
                        print('Shit')
            except socket.timeout as e:
                pass
            except KeyboardInterrupt as e:
                sys.exit(0)
            except Exception as e:
                print(e)
                
    def onClientObserved(self, socket, clients):
        data = socket.recv(1024)
        if len(data) == 0:
            clients.remove(socket)
        elif data:
            self.onClientEventObserved(socket, data.decode(Decoding.UTF_8))
            
    def onWorkerObserved(self, socket, workers):
        data = socket.recv(1024)
        if len(data) == 0:
            workers.remove(socket)
        elif data:
            self.onWorkerEventObserved(socket, data.decode(Decoding.UTF_8))
     
    def onClientEventObserved(self, socket, event):
        type = self.getEventType(event)
        if type == Event.STATUS:
            self.sendJobStatus(socket, event)
        else:
            self.enqueueJobs(socket, event)
            
    def onWorkerEventObserved(self, socket, event):
        type = self.getEventType(event)
        if type == Event.POLL:
            self.onJobPolling(socket)
        elif type == Event.DONE:
            self.onJobDone(event)
        else:
            print('Fuck')

    def onJobDone(self, event):
        id = int(event.split(Event.DONE + Delimiter.SPACE)[1])
        job = self.jobById(id)
        job.status = Status.DONE
        print('Job', str(id), 'is done')

    def onJobPolling(self, socket):
        job = self.getPendingJob()
        result = job.toString() if job else Event.NOT_FOUND
        socket.sendall(result.encode())
        job.status = Status.IN_PROGRESS 
            
    def getPendingJob(self):
        i = 0
        while (i < self.size()):
            job = self.queue[i]
            if (job.status == Status.PENDING):
                return job
            i += 1
        return None
      
    def enqueueJobs(self, socket, event):
        for work in event.split(Delimiter.JOB):
            if len(work) > 0:
                id = str(self.size())
                self.queue.append(Broker.Job(id, work))
                socket.sendall((id + Delimiter.NEW_LINE).encode())
                
    def sendJobStatus(self, socket, event):
        id = int(event.split(Delimiter.SPACE)[1])
        job = self.jobById(id)
        socket.sendall(job.status.encode())
    
    def jobById(self, id):
        return self.queue[id]
    
    def getEventType(self, event):
        return event.split(Delimiter.SPACE)[0]
    
    def size(self):
        return len(self.queue)
    
    def readOn(self, socket, registry):
        conn = socket.accept()                        
        conn.setblocking(False)
        registry.append(conn)

def main():
    Broker().run()

if __name__ == "__main__":
    main()