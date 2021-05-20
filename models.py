
class User():
    def __init__(self, username, email):
        self.username = username
        self.email = email

class Directory():
    def __init__(self, parent, dirname, size, owner, isShared, sharedBy):
        self.parent = parent
        self.dirname = dirname
        self.size = size
        self.owner = owner
        self.isShared = isShared
        self.sharedBy = sharedBy

class File():
    def __init__(self, parent, filename, type, size, time, owner, isShared, sharedBy):
        self.parent = parent
        self.filename = filename
        self.type = type
        self.size = size
        self.time = time
        self.owner = owner
        self.isShared = isShared
        self.sharedBy = sharedBy
