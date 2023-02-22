import socket
import time

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(('localhost', 8001))
    
    job = 'JOB xxx\nJOB ooo\n'
    client.send(job.encode())
    job = 'JOB xxx\nJOB ooo\n'
    client.send(job.encode())
    job = 'JOB xxx\nJOB ooo\n'
    client.send(job.encode())
    job = 'JOB xxx\nJOB ooo\n'
    client.send(job.encode())
    job = 'JOB xxx\nJOB ooo\n'
    client.send(job.encode())

    
    time.sleep(2)
    client.send('STATUS 1'.encode())
    data = client.recv(1024)
    print(data.decode('utf-8'))
    time.sleep(2)
    client.send('STATUS 2'.encode())
    data = client.recv(1024)
    print(data.decode('utf-8'))
    time.sleep(2)
    client.send('STATUS 3'.encode())
    data = client.recv(1024)
    print(data.decode('utf-8'))
    time.sleep(2)
    client.send('STATUS 4'.encode())
    data = client.recv(1024)
    print(data.decode('utf-8'))
    
        
    # i = 0
    # while i < 100000:
    #     req = ('STATUS ' + str(i)).encode()
    #     i += 1
    #     print(req)
    #     client.send(req)
        # i += 1
        # data = client.recv(1024)
        # if data:
        #     print('Job status as follows')
        #     # print(data.decode('utf-8'))
        # else:
        #     print('Fuck')