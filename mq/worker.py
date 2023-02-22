import socket
import syslog
import time

class Worker:
    def __init__(self):
        self.inProgress = False
        
    def poll(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as o:
            s.connect(('localhost', 8002))
            while True:
                # syslog.syslog(syslog.LOG_INFO, 'Fetching job')
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
                        # syslog.syslog(syslog.LOG_INFO, 'Starting job')
                        for t in texts:
                            time.sleep(0.25)
                            # o.sendto(t.encode(), ('localhost', 8002))
                            print(t)
                            # syslog.syslog(syslog.LOG_INFO, t)
                        s.send(('DONE ' + id).encode())
                        # syslog.syslog(syslog.LOG_INFO, 'Completed job')
                else:
                    print('Shit')
                    
Worker().poll()