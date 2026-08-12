"""加法ポテンシャル差付き Union-Find。"""


class WeightedUnionFind:
    r"""制約 ``potential[y] - potential[x] = weight`` を管理する。

    矛盾する制約を追加しようとした ``union`` は ``False`` を返し、状態を
    変更しない。未連結頂点間の ``diff`` は ``None``。各操作の償却計算量は
    :math:`O(\alpha(N))`、空間は :math:`O(N)`。

    Args:
        n: 0-indexed の要素数。0も許す。
    """

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n must be non-negative")
        self._parent = list(range(n))
        self._size = [1] * n
        # potential[x] - potential[parent[x]]
        self._diff_weight = [0] * n

    def find(self, x: int) -> int:
        """``x`` の代表元を返し、経路を圧縮する。"""
        if not 0 <= x < len(self._parent):
            raise IndexError("x out of range")
        path: list[int] = []
        vertex = x
        while self._parent[vertex] != vertex:
            path.append(vertex)
            vertex = self._parent[vertex]
        root = vertex
        accumulated = 0
        for vertex in reversed(path):
            accumulated += self._diff_weight[vertex]
            self._parent[vertex] = root
            self._diff_weight[vertex] = accumulated
        return root

    def weight(self, x: int) -> int:
        """代表元を0とした ``x`` の相対ポテンシャルを返す。"""
        self.find(x)
        return self._diff_weight[x]

    def union(self, x: int, y: int, weight: int) -> bool:
        """制約 ``potential[y] - potential[x] = weight`` を追加する。

        新しい成分を併合した場合と、既存制約と整合する場合は ``True``。
        既存制約と矛盾する場合だけ ``False`` を返す。
        """
        root_x = self.find(x)
        root_y = self.find(y)
        weight_x = self._diff_weight[x]
        weight_y = self._diff_weight[y]
        if root_x == root_y:
            return weight_y - weight_x == weight

        # root_y を root_x の子にしたときの potential[root_y]-potential[root_x]
        root_difference = weight + weight_x - weight_y
        if self._size[root_x] < self._size[root_y]:
            root_x, root_y = root_y, root_x
            root_difference = -root_difference
        self._parent[root_y] = root_x
        self._diff_weight[root_y] = root_difference
        self._size[root_x] += self._size[root_y]
        return True

    def same(self, x: int, y: int) -> bool:
        """``x`` と ``y`` が同じ成分なら ``True`` を返す。"""
        return self.find(x) == self.find(y)

    def diff(self, x: int, y: int) -> int | None:
        """``potential[y] - potential[x]``、未連結なら ``None`` を返す。"""
        if self.find(x) != self.find(y):
            return None
        return self._diff_weight[y] - self._diff_weight[x]

    def size(self, x: int) -> int:
        """``x`` の成分サイズを返す。"""
        return self._size[self.find(x)]
