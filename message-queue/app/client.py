import socket
import time

class Client:
    def __init__(self):
        self.sockets = [
            socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ]
        
    def connect(self):
        for socket in self.sockets:
            socket.connect(('localhost', 3000))
        return self
    
    def push(self, jobs):
        for job in jobs:
            for i, socket in enumerate(self.sockets):
                time.sleep(0.25)
                o = job + ' - client - ' + str(i)
                print('Client ' + str(i) + ' sending ' + o)
                socket.send(o.encode())

class Registry:
    def __init__(self):
        self.jobs = [
            'JOB go to the mall\n',
            'JOB clean up the room\n',
            'JOB get dressed\n',
            'JOB get out of bed\n'
        ]

    def all(self):
        return self.jobs;
        
class Pushing:
    def __init__(self, registry, client):
        self.registry = registry
        self.client = client
    
    def invoke(self):
        self.client.connect().push(self.registry.all())
            
Pushing(Registry(), Client()).invoke()
    



