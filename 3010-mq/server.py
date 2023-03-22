import socket
import select
import sys
from contants import Delimiter, Status, Event, Port, Decoding
    
class Broker:
    class Job:   
        def __init__(self, id, work):
            self.id = id
            self.work = work
            self.status = Status.PENDING
            
        def toString(self):
            return self.id + Delimiter.SPACE + self.work
        
    def __init__(
        self, 
        clientPort = Port.CLIENT, 
        workerPort = Port.WORKER, 
        host = Port.HOST
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
                readable, writable, exceptional = select.select(inputs + clients + workers, outputs, inputs + clients + workers, 3)
                print('Listening...')
                for r in readable:
                    if r is clientSocket:
                        self.readOn(r, clients)
                    elif r is workerSocket:
                        self.readOn(r, workers)
                    elif r in clients:
                        self.onObserveClient(r, clients)
                    elif r in workers:
                        self.onObserveWorker(r, workers)
                    else:
                        print('Readable does not exist')
            except socket.timeout as e:
                print('Time out')
            except KeyboardInterrupt as e:
                sys.exit(0)
            except Exception as e:
                print(e)
                
    def onObserveClient(self, socket, clients):
        data = socket.recv(1024)
        if len(data) == 0:
            clients.remove(socket)
        elif data:
            self.onObserveClientEvent(socket, data.decode(Decoding.UTF_8, 'ignore'))
            
    def onObserveWorker(self, socket, workers):
        data = socket.recv(1024)
        if len(data) == 0:
            workers.remove(socket)
        elif data:
            self.onObserveWorkerEvent(socket, data.decode(Decoding.UTF_8, 'ignore'))
     
    def onObserveClientEvent(self, socket, event):
        e = self.event(event)
        if e == Event.STATUS:
            self.sendJobStatus(socket, event)
        else:
            self.enqueueJobs(socket, event)
            
    def onObserveWorkerEvent(self, socket, event):
        e = self.event(event)
        if e == Event.POLL:
            self.onJobPolling(socket)
        elif e == Event.DONE:
            self.onJobDone(event)
        else:
            print('Event does not exist')

    def onJobDone(self, event):
        id = int(event.split(Event.DONE + Delimiter.SPACE)[1])
        job = self.jobById(id)
        job.status = Status.DONE
        print('Job', str(id), 'is done')

    def onJobPolling(self, socket):
        job = self.getPendingJob()
        if job:
            socket.sendall(job.toString().encode())
            job.status = Status.IN_PROGRESS
        else:
            socket.sendall(Event.NOT_FOUND.encode())
          
    def getPendingJob(self):
        i = 0
        while (i < self.size()):
            job = self.queue[i]
            if (job.status == Status.PENDING):
                return job
            i += 1
        return None
      
    def enqueueJobs(self, socket, event):
        for u in self.unitsOfWork(event):
            if len(u) > 0:
                id = str(self.size())
                self.queue.append(Broker.Job(id, u))
                socket.sendall((id + Delimiter.NEW_LINE).encode())

    def unitsOfWork(self, event):
        unitsOfWorks = event.split(Delimiter.JOB)
        unitsOfWorks[-1] = unitsOfWorks[-1].split(Delimiter.RETURN + Delimiter.NEW_LINE)[0]
        return unitsOfWorks
                
    def sendJobStatus(self, socket, event):
        id = int(event.split(Delimiter.SPACE)[1])
        job = self.jobById(id)
        result = 'Job with ID ' + str(id)
        result += ' has status of ' + job.status if job else ' is not found'
        socket.sendall(result.encode())
    
    def jobById(self, id):
        return None if self.outOfBounds(id) else self.queue[id]

    def outOfBounds(self, id):
        return id < 0 or id >= self.size()
    
    def event(self, event):
        return event.split(Delimiter.SPACE)[0]
    
    def size(self):
        return len(self.queue)
    
    def readOn(self, socket, registry):
        conn, addr = socket.accept()                        
        conn.setblocking(False)
        registry.append(conn)

def main():
    args = sys.argv
    print(args)
    if len(args) == 4:
        Broker(clientPort=int(args[1]), workerPort=int(args[2]), host=args[3]).run()
    elif len(args) == 3:
        Broker(clientPort=int(args[1]), workerPort=int(args[2])).run()
    else:
        Broker().run()

if __name__ == "__main__":
    main()