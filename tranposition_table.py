class TranspositionTable:
    class Entry:
        def __init__(self, key=0, val=0):
            self.key = key
            self.val = val

    def __init__(self, size):
        if size <= 0:
            raise ValueError("Size must be greater than 0")
        self.T = [self.Entry() for _ in range(size)]

    def index(self, key):
        return key % len(self.T)

    def reset(self):
        for i in range(len(self.T)):
            self.T[i] = self.Entry()

    def put(self, key, val):
        idx = self.index(key)
        self.T[idx].key = key
        self.T[idx].val = val

    def get(self, key):
        entry = self.T[self.index(key)]
        return entry.val if entry.key == key else None  
