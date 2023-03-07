class PathUtils:
    
    def hasId(path):
        return len(PathUtils.splitPath(path)) == 4

    def stripId(path):
        return int(PathUtils.splitPath(path)[3])
    
    def splitPath(path):
        return path.split('/')
    
    def extractUser(req):
        for o in req.split('\r\n'):
            if 'Cookie' in o:
                u = o.split(': ')[1].split('; ')[0].split('=')[1]
                return u
        return None