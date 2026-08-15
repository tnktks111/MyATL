r"""連結成分ごとの辺数・閉路・頂点重みを管理する Union-Find。"""

from collections.abc import Sequence
from typing import NamedTuple


class ComponentInfo(NamedTuple):
    """連結成分の集約情報。"""

    size: int
    edge_count: int
    extra_edge_count: int
    has_cycle: bool
    is_tree: bool
    weight_sum: int
    weight_max: int


class GraphUnionFind:
    r"""辺追加型の無向グラフについて連結成分の情報を管理する。

    自己ループと多重辺もそれぞれ1辺として数える。各操作の償却計算量は
    :math:`O(\alpha(N))`、空間計算量は :math:`O(N)`。

    Args:
        weights: 各頂点の整数重み。長さが頂点数になる。空列も許す。

    Notes:
        ``extra_edge_count(x)`` は、``x`` の成分を木にするために削除する
        必要がある辺の本数（閉路空間の次元）を返す。辺や頂点の削除、辺の
        重み、頂点重みの変更には対応しない。
    """

    def __init__(self, weights: Sequence[int]) -> None:
        self._parent = list(range(len(weights)))
        self._size = [1] * len(weights)
        self._edge_count = [0] * len(weights)
        self._weight_sum = list(weights)
        self._weight_max = list(weights)
        self._group_count = len(weights)

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

    def add_edge(self, x: int, y: int) -> bool:
        """無向辺 ``(x, y)`` を追加し、異なる成分を併合したかを返す。"""
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            self._edge_count[root_x] += 1
            return False

        if self._size[root_x] < self._size[root_y]:
            root_x, root_y = root_y, root_x
        self._parent[root_y] = root_x
        self._size[root_x] += self._size[root_y]
        self._edge_count[root_x] += self._edge_count[root_y] + 1
        self._weight_sum[root_x] += self._weight_sum[root_y]
        self._weight_max[root_x] = max(
            self._weight_max[root_x], self._weight_max[root_y]
        )
        self._group_count -= 1
        return True

    def same(self, x: int, y: int) -> bool:
        """``x`` と ``y`` が同じ連結成分なら ``True`` を返す。"""
        return self.find(x) == self.find(y)

    def size(self, x: int) -> int:
        """``x`` の成分の頂点数を返す。"""
        return self._size[self.find(x)]

    def edge_count(self, x: int) -> int:
        """``x`` の成分の辺数を返す。"""
        return self._edge_count[self.find(x)]

    def extra_edge_count(self, x: int) -> int:
        """``x`` の成分を木にするために削除すべき辺数を返す。"""
        root = self.find(x)
        return self._edge_count[root] - self._size[root] + 1

    def has_cycle(self, x: int) -> bool:
        """``x`` の成分が閉路を含むなら ``True`` を返す。"""
        return self.extra_edge_count(x) > 0

    def is_tree(self, x: int) -> bool:
        """``x`` の成分が木なら ``True`` を返す。孤立頂点も木とする。"""
        return self.extra_edge_count(x) == 0

    def weight_sum(self, x: int) -> int:
        """``x`` の成分に含まれる頂点重みの合計を返す。"""
        return self._weight_sum[self.find(x)]

    def weight_max(self, x: int) -> int:
        """``x`` の成分に含まれる頂点重みの最大値を返す。"""
        return self._weight_max[self.find(x)]

    def group_count(self) -> int:
        """現在の連結成分数を :math:`O(1)` で返す。"""
        return self._group_count

    def info(self, x: int) -> ComponentInfo:
        """``x`` の成分の全集約情報を返す。"""
        root = self.find(x)
        extra = self._edge_count[root] - self._size[root] + 1
        return ComponentInfo(
            size=self._size[root],
            edge_count=self._edge_count[root],
            extra_edge_count=extra,
            has_cycle=extra > 0,
            is_tree=extra == 0,
            weight_sum=self._weight_sum[root],
            weight_max=self._weight_max[root],
        )


__all__ = ["ComponentInfo", "GraphUnionFind"]
