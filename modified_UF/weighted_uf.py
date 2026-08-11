class WeightedUnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.diff_weight = [0] * n

    def find(self, x):
        if self.parent[x] == x:
            return x

        p = self.parent[x]
        self.parent[x] = self.find(p)
        self.diff_weight[x] += self.diff_weight[p]
        return self.parent[x]

    def weight(self, x):
        self.find(x)
        return self.diff_weight[x]

    def union(self, x, y, w):
        """
        potential[y] - potential[x] = w
        """
        rx = self.find(x)
        ry = self.find(y)

        wx = self.weight(x)
        wy = self.weight(y)

        if rx == ry:
            return wy - wx == w

        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
            w = -w
            wx, wy = wy, wx

        self.parent[ry] = rx
        self.diff_weight[ry] = w + wx - wy
        self.size[rx] += self.size[ry]
        return True

    def diff(self, x, y):
        """
        potential[y] - potential[x]
        """
        if self.find(x) != self.find(y):
            return None
        return self.weight(y) - self.weight(x)
