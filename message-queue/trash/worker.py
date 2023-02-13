import socket
import sys
import time

class Worker:
    def __init__(self):
        self.inProgress = False
        
    def poll(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 10001))
            while True:
                time.sleep(3)
                str = 'GET - Text'
                s.send(str.encode())
                
                # on job polled
                data = s.recv(1024)

                if not data:
                    print('Pending')
                if len(data) == '':
                    print('Shit')
                else:
                    print('Broker', data.decode())
                    # on job done
                    time.sleep(3)
                    str = 'POST job-is-done'
                    print(str)
                    s.send(str.encode())
    
    def onJobPolled(self):
        pass


Worker().poll()