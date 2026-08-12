"""削除されていない次の位置を探す Successor DSU。"""


class SuccessorDSU:
    r"""集合 ``{0, ..., n-1}`` の削除と successor query を処理する。

    ``erase(x)`` は位置 ``x`` を削除し、``next(x)`` は ``x`` 以上で未削除の
    最小位置を返す。存在しない場合は番兵 ``n`` を返す。重複削除も許す。
    各操作の償却計算量は :math:`O(\alpha(N))`、空間は :math:`O(N)`。

    Args:
        n: 位置数。0も許す。
    """

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n must be non-negative")
        self._n = n
        self._parent = list(range(n + 1))

    def _find(self, x: int) -> int:
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[x] != x:
            parent = self._parent[x]
            self._parent[x] = root
            x = parent
        return root

    def erase(self, x: int) -> bool:
        """``x`` を削除し、初回の削除なら ``True`` を返す。"""
        if not 0 <= x < self._n:
            raise IndexError("x out of range")
        if self._find(x) != x:
            return False
        self._parent[x] = self._find(x + 1)
        return True

    def next(self, x: int) -> int:
        """``x`` 以上の未削除位置、なければ ``n`` を返す。"""
        if not 0 <= x <= self._n:
            raise IndexError("x out of range")
        return self._find(x)
