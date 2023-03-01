import json
import socket
import threading

class Repo:
    
    def __init__(self):
        self.dirty = False
        self.records = self.load()
    
    def all(self):
        self.ensureRecordsFresh()
        return self.records
    
    def byId(self, id):
        self.ensureRecordsFresh()
        i = self.at(id)
        return self.records[i] if self.valid(i) else None

    def post(self, o):
        id = o['id']
        if self.byId(id):
            self.put(id, o)
        else:
            self.records.append(o)
            self.save()
    
    def put(self, id, o):
        i = self.at(id)
        if (self.valid(i)):
            self.records[i] = o
            self.save()
    
    def delete(self, id):
        i = self.at(id)
        if (self.valid(i)):
            del self.records[i]
            self.save()
            
    def sort(self):
        self.records = sorted(self.records, key = lambda o: o['id'])

    def at(self, id: int):
        for i, o in enumerate(self.records):
            print(id, o['id'], o['id'] == id)
            if (o['id'] == id):
                return i
        return -1
    
    def ensureRecordsFresh(self):
        if self.dirty:
            self.records = self.load()
            
    def valid(self, i):
        return i != -1
            
    def load(self):
        try:
            with open('tweets.json', 'r') as f:
                result = json.load(f)
            self.dirty = False
        except (FileNotFoundError, json.JSONDecodeError):
            result = []
        return result
    
    def save(self):
        self.sort()
        with open('tweets.json', 'w') as f:
            json.dump(self.records, f)
        self.dirty = True

class RESTful:
    
    def __init__(self, repo):
        self.repo = repo
    
    def all(self):
        return self.repo.all()
    
    def byId(self, id: int):
        return self.repo.at(id)
    
    def post(self, o):
        self.repo.post(o)
        
    def put(self, id: int, o):
        self.repo.put(id, o)
    
    def delete(self, id: int):
        self.repo.delete(id)

class API:
    def __init__(self, method, path, body):
        self.method = method
        self.path = path
        self.body = body
        self.restful = RESTful(Repo()) # TODO: refactor to DI

    def of(request):
        method, path, v = request.split('\n')[0].split()
        body = request.split('\r\n\r\n')[1]
        return API(method, path, body)

    def invoke(self):
        if self.method == 'GET':
            self.usingIdOr(lambda: self.byId(), lambda: self.all())
        elif self.method == 'POST':
            self.post()
        elif self.method == 'PUT':
            self.usingId(lambda: self.put())
        elif self.method == 'DELETE':
            self.usingId(lambda: self.delete())
        else:
            print('Fuck method')

    def delete(self):
        self.restful.delete(self.stripId())
        print(self.restful.all())

    def put(self):
        id = self.stripId()
        o = json.loads(self.body)
        print(id, o)
        if o['id'] == id:
            self.restful.put(id, o)
        else:
            print('Url param does not match id in body')
        print(self.restful.all())

    def post(self):
        print('POSTing')
        o = json.loads(self.body)
        print(o)
        self.restful.post(o)
        print(self.restful.all())

    def all(self):
        print(self.restful.all())

    def byId(self):
        print(self.restful.byId(self.stripId()))
        
    def usingId(self, f):
        if self.idInPath():
            f()
    
    def usingIdOr(self, x, y):
        if self.idInPath():
            x()
        else:
            y()
            
    def idInPath(self):
        return len(self.splitPath()) == 3
    
    def stripId(self):
        return int(self.splitPath()[2])
    
    def splitPath(self):
        return self.path.split('/')
    
class Server:
    
    def __init__(self, port = 8080, host = 'localhost'):
        self.port = port
        self.host = host
    
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self.config(s)
            self.run(s)
            
    def config(self, s):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen()
        
    def run(self, socket):
        while True:
            conn, addr = socket.accept()
            print(f'Connected to {addr}')
            t = threading.Thread(target=self.onObserve, args=(conn,))
            t.start()

    def onObserve(self, client):
        req = client.recv(1024).decode()
        path = req.split('\n')[0].split()[1]
        if '/tweets' in path:
            API.of(req).invoke()
        else:
            print('Fuck path')
    
if __name__ == '__main__':
    Server().start()