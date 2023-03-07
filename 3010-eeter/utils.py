class PathUtils:
    
    def hasId(path):
        return len(PathUtils.splitPath(path)) == 4

    def stripId(path):
        return int(PathUtils.splitPath(path)[3])
    
    def splitPath(path):
        return path.split('/')