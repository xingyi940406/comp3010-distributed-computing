class Delimiter:
    EMPTY = ''
    SPACE = ' '
    NEW_LINE = '\n'
    RETURN = '\r'
    JOB = '\r\nJOB '

class Event:
    JOB = 'JOB'
    POLL = 'POLL'
    STATUS = 'STATUS'
    DONE = 'DONE'
    NOT_FOUND = 'NOT_FOUND'
    
class Status:
    DONE = 'Done'
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    
class Port:
    CLIENT = 8001
    WORKER = 8002
    HOST = 'localhost'
    OUTPUTS = 30000
    SYSLOG = 30001
    
class Decoding:
    UTF_8 = 'utf-8'