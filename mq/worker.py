from contants import Event, Network, Delimiter
import socket
import time

class Worker:
    def __init__(self):
        self.inProgress = False
    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as workerSocket, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as logSocket:
            self.connectOrRetry(workerSocket)
            while True:
                try:
                    self.poll(workerSocket, logSocket) 
                except socket.error:
                    workerSocket = socket.socket()
                    self.connectOrRetry(workerSocket)

    def connectOrRetry(self, workerSocket):
        connected = False
        while not connected:
            try:
                print('Trying to connect...')
                workerSocket.connect((Network.HOST, 8002))
                print('Connected')
                connected = True
            except socket.error:
                print('Reconnect after 1 sec')
                time.sleep(1)
                        
    def poll(self, workerSocket, logSocket):
        self.log(logSocket, 'Polling job')
        workerSocket.send((Event.POLL + ' job').encode())
        data = workerSocket.recv(1024) # Get stuck here
        if data:
            result = data.decode()
            if result == Event.NOT_FOUND:
                self.onJobNotFound()
            else:
                self.onJobPolled(workerSocket, logSocket, result)
        else:
            print('Shit')

    def onJobNotFound(self):
        print('Job not found')
        time.sleep(1)
                    
    def onJobPolled(self, workerSocket, logSocket, result):
        id = self.jobId(result)
        self.log(logSocket, 'Starting job ' + id)
        for w in self.words(result, id):
            time.sleep(0.25)
            print(w)
            logSocket.sendto(w.encode(), (Network.HOST, 3000))
        self.onJobDone(workerSocket, logSocket, id)

    def onJobDone(self, workerSocket, logSocket, id):
        workerSocket.send((Event.DONE + Delimiter.SPACE + id).encode())
        self.log(logSocket, 'Completed job ' + id)

    def words(self, result, id):
        return result.replace(id + Delimiter.SPACE, Delimiter.EMPTY).split(Delimiter.SPACE)

    def jobId(self, result):
        return result.split(Delimiter.SPACE)[0]           
    
    def log(self, socket, log):
        socket.sendto(log.encode(), (Network.HOST, Network.SYSLOG))
        print(log)
                    
Worker().run()