import sys
from contants import Event, Port, Delimiter
import socket
import time

class Worker:
    def __init__(self, 
        workerPort = Port.WORKER, 
        outputsPort = Port.OUTPUTS, 
        logsPort = Port.SYSLOG, 
        host = Port.HOST
    ):
        self.workerPort = workerPort
        self.logsPort = logsPort
        self.outputsPort = outputsPort
        self.host = host
        
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
                workerSocket.connect((self.host, self.workerPort))
                print('Connected')
                connected = True
            except socket.error:
                print('Reconnect after 1 sec')
                time.sleep(1)
                        
    def poll(self, workerSocket, logSocket):
        self.log(logSocket, 'Polling job')
        workerSocket.send((Event.POLL + ' job').encode())
        data = workerSocket.recv(1024)
        if data:
            result = data.decode()
            if result == Event.NOT_FOUND:
                self.onJobNotFound()
            else:
                self.onJobPolled(workerSocket, logSocket, result)
        else:
            print('No data received')

    def onJobNotFound(self):
        print('Job not found')
        time.sleep(1)
                    
    def onJobPolled(self, workerSocket, logSocket, result):
        id = self.jobId(result)
        self.log(logSocket, 'Starting job ' + id)
        for w in self.words(result, id):
            time.sleep(0.25)
            print(w)
            logSocket.sendto(w.encode(), (self.host, self.outputsPort))
        self.onJobDone(workerSocket, logSocket, id)

    def onJobDone(self, workerSocket, logSocket, id):
        workerSocket.send((Event.DONE + Delimiter.SPACE + id).encode())
        self.log(logSocket, 'Completed job ' + id)

    def words(self, result, id):
        return result.replace(id + Delimiter.SPACE, Delimiter.EMPTY).split(Delimiter.SPACE)

    def jobId(self, result):
        return result.split(Delimiter.SPACE)[0]           
    
    def log(self, socket, log):
        socket.sendto(log.encode(), (self.host, self.logsPort))
        print(log)

def main():
    args = sys.argv
    if len(args) == 4:
        brokerIpAndPort = args[1]
        arr = brokerIpAndPort.split(':')
        Worker(workerPort=int(arr[1]), outputsPort=int(args[2]), logsPort=int(args[3]), host=arr[0]).run()
    else:
        Worker().run()

if __name__ == "__main__":
    main()