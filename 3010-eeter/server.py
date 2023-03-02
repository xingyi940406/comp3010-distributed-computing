import json
import socket
import threading

class Repo:
    
    def __init__(self, db):
        self.db = db
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
            with open(self.db, 'r') as f:
                result = json.load(f)
            self.dirty = False
        except (FileNotFoundError, json.JSONDecodeError):
            result = []
        return result
    
    def save(self):
        self.sort()
        with open(self.db, 'w') as f:
            json.dump(self.records, f, indent=4)
        self.dirty = True

class RESTful:
    
    def __init__(self, repo: Repo):
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
        
class UI:
    def __init__(self, socket):
        self.socket = socket
    
    def mount(self):
        try:
            with open('index.html', 'r') as f:
                ui = f.read()
            res = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{ui}'
            self.socket.send(res.encode())
        except FileNotFoundError:
            print("File not found")
        except IOError:
            print("IO error")
        except Exception as e:
            print(e)

class Signin:
    def __init__(self, socket, method, path, body):
        self.socket = socket
        self.method = method
        self.path = path
        self.body = body
        self.restful = RESTful(Repo('users.json'))
        self.cookies = RESTful(Repo('cookies.json'))

    def of(socket, request):
        method, path, v = request.split('\n')[0].split()
        body = request.split('\r\n\r\n')[1]
        return Signin(socket, method, path, body)
    
    def invoke(self):
        u = self.user()
        if u:
            username = u['username']
            cookie = { 'id': 1, 'user': username  }
            self.cookies.post(cookie)
            self.socket.sendall(b'HTTP/1.1 200 OK\r\nSet-Cookie: user=' + username.encode() + b'\r\n\r\n')
            print('Signed in')
        else:
            self.socket.sendall(b'HTTP/1.1 401 Unauthorized\r\nContent-Type: text/plain\r\n\r\nFailed to sign in')
            
    def user(self):
        for u in self.restful.all():
            if (self.credentialsMatched(u)):
                return u
        return None

    def credentialsMatched(self, user):
        username, password = self.credentials()
        return user['username'] == username and user['password'] == password

    def credentials(self):
        print(self.body)
        user = json.loads(self.body)
        return (user['username'], user['password'])
        
class Dashboard:
    def __init__(self, socket, method, path, body):
        self.socket = socket
        self.method = method
        self.path = path
        self.body = body
        self.restful = RESTful(Repo('posts.json'))

    def of(socket, request):
        method, path, v = request.split('\n')[0].split()
        body = request.split('\r\n\r\n')[1]
        return Dashboard(socket, method, path, body)
        
    def invoke(self):
        if self.method == 'GET':
            self.atIdOr(lambda: self.byId(), lambda: self.all())
        elif self.method == 'POST':
            self.post()
        elif self.method == 'PUT':
            self.atId(lambda: self.put())
        elif self.method == 'DELETE':
            self.atId(lambda: self.delete())
        else:
            print('Fuck method')
            
    def jsonify(self, o):
        return json.dumps(o)

    def all(self):
        all = self.restful.all()
        body = self.jsonify(all)
        ok = self.ok(body)
        print(ok)
        self.socket.send(ok.encode())
        
    def byId(self):
        print(self.restful.byId(self.stripId()))

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
        
    def atId(self, f):
        if self.idInPath():
            f()
    
    def atIdOr(self, x, y):
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

    def ok(self, body):
        return f'HTTP/1.1 200 OK\nContent-Type: application/json\r\n\n{body}'

class Server:
    
    def __init__(self, port = 8080, host = 'localhost'):
        self.port = port
        self.host = host
    
    def start(self):
        print('http://localhost:8080/')
        print('http://localhost:8080/tweets')
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

    def onObserve(self, socket):
        req = socket.recv(1024).decode()
        path = req.split('\n')[0].split()[1]
        if '/' == path:
            UI(socket).mount()
        elif '/login' == path:
            Signin.of(socket, req).invoke()
        elif '/tweets' in path:
            Dashboard.of(socket, req).invoke()
        else:
            print('Fuck path', path)
    
if __name__ == '__main__':
    Server().start()