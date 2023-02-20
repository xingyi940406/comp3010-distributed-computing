import socket
import sys
import time

class Worker:
    def __init__(self):
        self.inProgress = False
        
    def poll(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 8001))
            
            while True:
                print('Start')
                str = 'GET - Text'
                s.send(str.encode())
                print('Start sending')
                
                # on job polled
                data = s.recv(4096) # Get stuck here
                
                print('After polling')

                if not data:
                    print('Pending')
                if len(data) == '':
                    print('Shit')
                else:
                    print('Broker', data.decode())
                    # on job done
                    str = 'POST job-is-done'
                    print(str)
                    s.send(str.encode())
                    print('After sending')
                    
                print('End')
    
    def onJobPolled(self):
        pass


Worker().poll()