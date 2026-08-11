class myUnionFind:
    def __init__(self, n):
        self.n = n
        self.parent = [i for i in range(n)]
        self.size = [1] * n
    def find(self, x):
        if self.parent[x] == x:
            return x
        self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, x, y):
        a = self.find(x)
        b = self.find(y)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.size[a] += self.size[b]
        self.parent[b] = a
        self.n -= 1
        return True
    def same(self, x, y):
        return self.find(x) == self.find(y)
    def get_self_size(self):
        return self.size