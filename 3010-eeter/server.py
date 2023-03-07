import json
import socket
import threading
from utils import PathUtils

class Repo:
    
    def __init__(self, db):
        self.db = db
        self.records = self.load()
    
    def all(self):
        return self.records
    
    def byId(self, id):
        i = self.at(id)
        return self.records[i] if self.valid(i) else None

    def post(self, o):
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

    def at(self, id: int):
        for i, o in enumerate(self.records):
            if (o['id'] == id):
                return i
        return -1
            
    def valid(self, i):
        return i != -1
            
    def load(self):
        try:
            with open(self.pathToDb(), 'r') as f:
                result = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            result = []
        except IOError:
            print("IO error")
        except Exception as e:
            print(e)
        return result
    
    def save(self):
        try:
            with open(self.pathToDb(), 'w') as f:
                json.dump(self.records, f, indent=4)
            self.reload()
        except IOError:
            print("IO error")
        except Exception as e:
            print(e)
        
    def reload(self):
        self.records = self.load()
        
    def pathToDb(self):
        return self.db

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
            self.socket.sendall(res.encode())
        except FileNotFoundError:
            print("UI file not found")
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
            print("Static file not found")
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
            self.signin(u)
        else:
            self.socket.sendall(b'HTTP/1.1 401 Unauthorized\r\nContent-Type: text/plain\r\n\r\nFailed to sign in')

    def signin(self, u):
        username = u['username']
        self.cookies.post({ 'id': 1, 'user': username })
        self.reply({ 'user': username })
            
    def register(self):
        u = self.user()
        if u:
            self.signin(u)
        else:
            username, password = self.credentials()
            self.users.post({ 'id': self.nextId(), 'username': username, 'password': password })
            self.cookies.post({ 'id': 1, 'user': username })
            self.reply({  'user': username })
            
    def nextId(self):
        all = self.users.all()
        if len(all) == 0:
            return 1
        return max(all, key=lambda o: o['id'])['id'] + 1
            
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
            
    def atId(self, f):
        if PathUtils.hasId(self.path):
            f()
    
    def atIdOrElse(self, f, orElse):
        if PathUtils.hasId(self.path):
            f()
        else:
            orElse()
            
    def all(self):
        self.reply(self.restful.all())
        
    def byId(self):
        self.reply(self.restful.byId(PathUtils.stripId(self.path)))

    def delete(self):
        self.restful.delete(PathUtils.stripId(self.path))
        self.reply('')

    def put(self):
        id = PathUtils.stripId(self.path)
        o = json.loads(self.body)
        if o['id'] == id:
            self.restful.put(id, o)
            self.reply('')
        else:
            self.socket.sendall(b'HTTP/1.1 404 Bad Request\r\nContent-Type: text/plain\r\n\r\nUrl param does not match object id in the request body')
    
    def post(self):
        body = json.loads(self.body)
        o = {
            'id': self.nextId(),
            'content': body['content'],
            'author': body['author']
        }
        self.restful.post(json.loads(json.dumps(o)))
        self.reply('')
        
    def nextId(self):
        all = self.restful.all()
        if len(all) == 0:
            return 1
        return max(all, key=lambda o: o['id'])['id'] + 1
    
    def reply(self, o):
        self.socket.sendall(self.ok(json.dumps(o)).encode())

    def ok(self, body):
        return f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\n{body}'
    

class HttpRequest:
    
    def split(req):
        method, path, v = req.split('\n')[0].split()
        body = req.split('\r\n\r\n')[1]
        return (method, path, body, v)

class Server:
    
    def __init__(self, port = 3000, host = 'localhost'):
        self.port = port
        self.host = host
    
    def run(self):
        print('http://localhost:3000/')
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        while True:
            client, addr = server.accept()
            print(f'Connected to {addr}')
            t = threading.Thread(target=self.onObserve, args=(client,))
            t.start()

    def onObserve(self, client):
        req = client.recv(1024).decode()
        path = self.extractPath(req)
        
        if '/' == path:
            UI(client).mount()
        elif '/register' == path:
            Signin.of(client, req).register()
        elif '/login' == path:
            Signin.of(client, req).invoke()
        elif '/logout' == path:
            Signout.of(client, req).invoke()
        elif '/images' in path:
            Pictures.of(client, req).invoke()
        elif '/tweets' in path:
            Posts.of(client, req).invoke()
        elif '/favicon.ico' in path:
            client.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n")
        else:
            client.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 13\r\n\r\n404 Not Found")
            
        client.shutdown(socket.SHUT_RDWR)
        client.close()

    def extractPath(self, req):
        return req.split('\n')[0].split()[1]
    
if __name__ == '__main__':
    Server().run()