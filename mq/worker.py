import socket
import time

class Worker:
    def __init__(self):
        self.inProgress = False
        
    def poll(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as o:
            s.connect(('localhost', 8002))
            while True:
                o.sendto('Fetching job'.encode(), ('localhost', 12345))
                s.send('POLL job'.encode())
                data = s.recv(1024) # Get stuck here
                if data:
                    result = data.decode()
                    if result == 'NOT_FOUND':
                        continue
                    else:
                        id = result.split(' ')[0]
                        text = result.replace(id + ' ', '')
                        texts = text.split(' ')
                        o.sendto('Starting job'.encode(), ('localhost', 12345))
                        for t in texts:
                            time.sleep(0.25)
                            print(t)
                        s.send(('DONE ' + id).encode())
                        o.sendto('Completed job'.encode(), ('localhost', 12345))
                else:
                    print('Shit')
                    
Worker().poll()