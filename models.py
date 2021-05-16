
class User():
    def __init__(self, username, email):
        self.username = username
        self.email = email

class Directory():
    def __init__(self, parent, dirname, size):
        self.parent = parent
        self.dirname = dirname
        self.size = size

class File():
    def __init__(self, parent, filename, type, size, time):
        self.parent = parent
        self.filename = filename
        self.type = type
        self.size = size
        self.time = time
