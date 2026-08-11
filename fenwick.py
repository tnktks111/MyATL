"""
Fenwick木

長さ N の配列 A に対して、
A[i] に x を足す
A[0] + A[1] + ... + A[i] を求める
をどちらも O(log N) でできる。
"""

class Fenwick_Tree:
    def __init__(self, n):
        self._n = n
        self.data = [0] * n
    
    def add(self, p, x):
        """
        A[p] += x
        """
        assert 0 <= p < self._n
        p += 1
        while p <= self._n:
            self.data[p - 1] += x
            p += p & -p
    
    def sum(self, l, r):
        """
        [l, r)の区間和を返す
        A[l] + ... + A[r - 1]
        """
        assert 0 <= l <= r <= self._n
        return self._sum(r) - self._sum(l)
    
    def _sum(self, r):
        """
        [0, r)の区間和を返す
        A[0] + ... + A[r - 1]
        """
        s = 0
        while r > 0:
            s += self.data[r - 1]
            r -= r & -r
        return s
    
    def lower_bound(self, w):
        """
        _sum(x) < w となる最大の x を返す
        
        注意: すべての要素が非負の場合にのみ正しく動作する。
        """
        if w <= 0:
            return 0 # _sum(0) = 0 なので w <= 0 の条件を満たせない
        
        x = 0
        bit = 1
        while bit < self._n:
            bit <<= 1
        while bit > 0:
            if x + bit <= self._n and self.data[x + bit - 1] < w:
                w -= self.data[x + bit - 1]
                x += bit
            bit >>= 1
        return x
    
    def upper_bound(self, w):
        """
        _sum(x) <= w となる最大の x を返す
        これは、0-indexed で「w+1 番目の要素がある index」を返す。
        ただし w は 0-indexed の順位として見る。

        注意: すべての要素が非負の場合にのみ正しく動作する。
        """
        if w < 0:
            return 0
        x = 0
        bit = 1
        while bit < self._n:
            bit <<= 1
        while bit > 0:
            if x + bit <= self._n and self.data[x + bit - 1] <= w:
                w -= self.data[x + bit - 1]
                x += bit
            bit >>= 1
        return x