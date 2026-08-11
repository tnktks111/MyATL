class SuccessorDSU:
    def __init__(self, n):
        self.parent = list(range(n + 1))

    def find(self, x):
        if self.parent[x] == x:
            return x
        self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def erase(self, x):
        self.parent[x] = self.find(x + 1)

    def next(self, x):
        return self.find(x)
