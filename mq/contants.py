class Delimiter:
    EMPTY = ''
    SPACE = ' '
    NEW_LINE = '\n'
    JOB = '\r\nJOB '

class Request:
    JOB = 'JOB'
    POLL = 'POLL'
    STATUS = 'STATUS'
    DONE = 'DONE'
    NOT_FOUND = 'NOT_FOUND'
    
class Status:
    DONE = 'Done'
    PENDING = 'Pending'
    
class Connection:
    CLIENT_PORT = 8001
    WORKER_PORT = 8002
    HOST = 'localhost'
    
class Decoding:
    UTF_8 = 'utf-8'