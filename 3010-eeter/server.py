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
        o = self.records
        print(o)
        return o
    
    def byId(self, id):
        self.ensureRecordsFresh()
        i = self.at(id)
        o = self.records[i] if self.valid(i) else None
        print(o)
        return o

    def post(self, o):
        id = o['id']
        if self.byId(id):
            self.put(id, o)
        else:
            self.records.append(o)
            self.save()
        print('Saved')
    
    def put(self, id, o):
        i = self.at(id)
        if (self.valid(i)):
            self.records[i] = o
            self.save()
        print('Saved')
    
    def delete(self, id):
        i = self.at(id)
        if (self.valid(i)):
            del self.records[i]
            self.save()
        print('Saved')
            
    def sort(self):
        self.records = sorted(self.records, key = lambda o: o['id'])

    def at(self, id: int):
        for i, o in enumerate(self.records):
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
        o = self.repo.all()
        print('Repo -', o)
        return o
    
    def byId(self, id: int):
        o = self.repo.at(id)
        print('Repo -', o)
        return o
    
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
            
class Pictures:
    
    def __init__(self, socket, method, path, body):
        self.socket = socket
        self.socket = socket
        self.method = method
        self.path = path
        self.body = body
    
    def of(socket, req):
        method, path, body, v = HttpRequest.split(req)
        return Pictures(socket, method, path, body)

    def extractTitle(self):
        return self.path.split('/')[2]
    
    def invoke(self):
        try:
            with open(self.extractTitle() +'.jpeg', 'rb') as f:
                img = f.read()
            res = f'HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n'
            self.socket.sendall(res.encode('utf-8') + img)
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
        self.users = RESTful(Repo('users.json'))
        self.cookies = RESTful(Repo('cookies.json'))

    def of(socket, req):
        method, path, body, v = HttpRequest.split(req)
        return Signin(socket, method, path, body)
    
    def invoke(self):
        u = self.user()
        if u:
            username = u['username']
            self.cookies.post({ 
                'id': 1, 
                'user': username
            })
            self.reply({ 
                'user': username 
            })
        else:
            self.socket.sendall(b'HTTP/1.1 401 Unauthorized\r\nContent-Type: text/plain\r\n\r\nFailed to sign in')
            
    def register(self):
        u = self.user()
        if u:
            self.invoke()
        else:
            username, password = self.credentials()
            self.users.post({
                'id': 50,
                'username': username,
                'password': password
            })
            self.cookies.post({ 
                'id': 1,
                'user': username  
            })
            self.reply({ 
                'user': username 
            })
            
    def reply(self, o):
        user = o['user']
        res = f'HTTP/1.1 200 OK\r\nSet-Cookie: user={user}\r\n\r\n{json.dumps(o)}'
        self.socket.sendall(res.encode())
    
    def user(self):
        for u in self.users.all():
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
  
class Signout:
    
    def __init__(self, socket, method, path, body):
        self.socket = socket
        self.method = method
        self.path = path
        self.body = body
        self.restful = RESTful(Repo('users.json'))
        self.cookies = RESTful(Repo('cookies.json'))
    
    def of(socket, req):
        method, path, body, v = HttpRequest.split(req)
        return Signout(socket, method, path, body)
        
    def invoke(self):
        user = json.loads(self.body)['user']
        for c in self.cookies.all():
            if (c['user'] == user):
                self.cookies.delete(c['id'])
        return self.socket.sendall(self.ok().encode())
    
    def ok(self):
        return f'HTTP/1.1 200 OK\nContent-Type: application/json\r\n\r\n'
      
class Posts:
    
    def __init__(self, socket, method, path, body):
        self.socket = socket
        self.method = method
        self.path = path
        self.body = self.strip(body)
        self.restful = RESTful(Repo('posts.json'))
        
    def strip(self, body):
        i = body.find("{")
        j = body.find("}") + 1
        return body[i:j]

    def of(socket, req):
        method, path, body, v = HttpRequest.split(req)
        return Posts(socket, method, path, body)
        
    def invoke(self):
        if self.method == 'GET':
            self.atIdOrElse(lambda: self.byId(), lambda: self.all())
        elif self.method == 'POST':
            self.post()
        elif self.method == 'PUT':
            self.atId(lambda: self.put())
        elif self.method == 'DELETE':
            self.atId(lambda: self.delete())
        else:
            print('Invalid HTTP method')
            
    def all(self):
        self.reply(self.restful.all())
        print('Sent posts')
        
    def byId(self):
        self.reply(self.restful.byId(self.stripId()))

    def delete(self):
        self.restful.delete(self.stripId())
        self.all()

    def put(self):
        id = self.stripId()
        o = json.loads(self.body)
        if o['id'] == id:
            self.restful.put(id, o)
            self.all()
        else:
            self.socket.sendall(b'HTTP/1.1 404 Bad Request\r\nContent-Type: text/plain\r\n\r\nUrl param does not match object id in the request body')
    
    def post(self):
        body = json.loads(self.body)
        o = {
            'id': 50,
            'content': body['content'],
            'author': body['author']
        }
        self.restful.post(json.loads(json.dumps(o)))
        self.all()
        
    def reply(self, o):
        self.socket.send(self.ok(self.jsonify(o)).encode())
        
    def jsonify(self, o):
        return json.dumps(o)

    def ok(self, body):
        return f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\n{body}'
        
    def atId(self, f):
        if self.idInPath():
            f()
    
    def atIdOrElse(self, f, orElse):
        if self.idInPath():
            f()
        else:
            orElse()
            
    def idInPath(self):
        return len(self.splitPath()) == 3
    
    def stripId(self):
        return int(self.splitPath()[2])
    
    def splitPath(self):
        return self.path.split('/')

class HttpRequest:
    
    def split(req):
        method, path, v = req.split('\n')[0].split()
        body = req.split('\r\n\r\n')[1]
        return (method, path, body, v)

class Server:
    
    def __init__(self, port = 8080, host = 'localhost'):
        self.port = port
        self.host = host
    
    def start(self):
        print('http://localhost:8080')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                print(f'Connected to {addr}')
                t = threading.Thread(target=self.onObserve, args=(conn,))
                t.start()

    def onObserve(self, socket):
        req = socket.recv(1024).decode()
        if 'favicon.ico' in req:
            return
        path = req.split('\n')[0].split()[1]
        if '/' == path:
            UI(socket).mount()
        elif '/register' == path:
            Signin.of(socket, req).register()
        elif '/login' == path:
            Signin.of(socket, req).invoke()
        elif '/logout' == path:
            Signout.of(socket, req).invoke()
        elif '/images' in path:
            Pictures.of(socket, req).invoke()
        elif '/tweets' in path:
            Posts.of(socket, req).invoke()
        else:
            print('Invalid path', path)
    
if __name__ == '__main__':
    Server().start()