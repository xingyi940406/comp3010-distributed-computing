import socket
import time

class Worker:
    def __init__(self):
        self.inProgress = False
    
    # TODO - Reconnets if disconnected
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as workerSocket, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as logSocket:
            self.tryConnect(workerSocket)
            while True:
                try:
                    self.poll(workerSocket, logSocket) 
                except socket.error:
                    workerSocket = socket.socket()
                    self.tryConnect(workerSocket)

    def tryConnect(self, workerSocket):
        connected = False
        while not connected:
            try:
                print('Trying to connect...')
                workerSocket.connect(('localhost', 8002))
                print('Connected')
                connected = True
            except socket.error:
                print('Reconnect after 1 sec')
                time.sleep(1)
                        
    def poll(self, workerSocket, logSocket):
        self.log(logSocket, 'Polling job')
        workerSocket.send('POLL job'.encode())
        data = workerSocket.recv(1024) # Get stuck here
        if data:
            result = data.decode()
            if result == 'NOT_FOUND':
                print('Job not found')
                time.sleep(1)
            else:
                self.onJobPolled(workerSocket, logSocket, result)
        else:
            print('Shit')
                    
    def onJobPolled(self, workerSocket, logSocket, result):
        id = self.jobId(result)
        self.log(logSocket, 'Starting job ' + id)
        for w in self.words(result, id):
            time.sleep(0.25)
            print(w)
            logSocket.sendto(w.encode(), ('localhost', 3000))
        workerSocket.send(('DONE ' + id).encode())
        self.log(logSocket, 'Completed job ' + id)

    def words(self, result, id):
        return result.replace(id + ' ', '').split(' ')

    def jobId(self, result):
        return result.split(' ')[0]           
    
    def log(self, socket, log):
        socket.sendto(log.encode(), ('localhost', 12345))
        print(log)
                    
Worker().run()