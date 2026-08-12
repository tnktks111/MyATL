r"""Disjoint Set Union (Union-Find).

0-indexed の要素を連結成分に分割して管理する。経路圧縮と union by size
により、各操作の償却計算量は :math:`O(\alpha(N))`、空間計算量は
:math:`O(N)` である。
"""


class UnionFind:
    r"""無向グラフの連結性を管理する Union-Find。

    Args:
        n: 要素数。要素は ``0 <= x < n``。

    Notes:
        ``union(x, y)`` は、すでに同じ成分なら ``False``、実際に併合した
        ときだけ ``True`` を返す。``groups()`` は :math:`O(N\alpha(N))`。
    """

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n must be non-negative")
        self._parent = list(range(n))
        self._size = [1] * n
        self._group_count = n

    def find(self, x: int) -> int:
        r"""``x`` の代表元を返す。償却 :math:`O(\alpha(N))`。"""
        if not 0 <= x < len(self._parent):
            raise IndexError("x out of range")
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[x] != x:
            parent = self._parent[x]
            self._parent[x] = root
            x = parent
        return root

    def union(self, x: int, y: int) -> bool:
        """``x`` と ``y`` を併合し、成分が変化したかを返す。"""
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return False
        if self._size[root_x] < self._size[root_y]:
            root_x, root_y = root_y, root_x
        self._parent[root_y] = root_x
        self._size[root_x] += self._size[root_y]
        self._group_count -= 1
        return True

    def same(self, x: int, y: int) -> bool:
        """``x`` と ``y`` が同じ成分なら ``True`` を返す。"""
        return self.find(x) == self.find(y)

    def size(self, x: int) -> int:
        """``x`` が属する成分の要素数を返す。"""
        return self._size[self.find(x)]

    def group_count(self) -> int:
        """現在の連結成分数を :math:`O(1)` で返す。"""
        return self._group_count

    def groups(self) -> list[list[int]]:
        """全成分を要素番号順のリストとして返す。"""
        result: dict[int, list[int]] = {}
        for vertex in range(len(self._parent)):
            result.setdefault(self.find(vertex), []).append(vertex)
        return list(result.values())

__all__ = ["UnionFind"]
