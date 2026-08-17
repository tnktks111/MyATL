r"""重み付き無向グラフの Kruskal Reconstruction Tree。"""

from collections.abc import Sequence


class KruskalReconstructionTree:
    r"""Kruskal法の連結成分併合過程を表す二分木（非連結なら森）。

    ノード ``0 <= v < n`` は元の頂点で、以降は辺を採用して2成分を併合する
    たびに作られる内部ノードである。内部ノードの重みは、その2成分が初めて
    連結した辺の重みになる。自己ループと、すでに同じ成分を結ぶ辺は無視する。

    構築は :math:`O(M\log M + N\log N)`、保持する空間は
    :math:`O(N\log N)`。``lca`` と ``connection_weight`` は二分累乗表の
    構築後 :math:`O(\log N)`。

    Args:
        n: 元グラフの頂点数。0も許す。
        edges: ``(u, v, weight)`` からなる無向辺列。負重み、多重辺を許す。
    """

    def __init__(
        self, n: int, edges: Sequence[tuple[int, int, int]] = ()
    ) -> None:
        if n < 0:
            raise ValueError("n must be non-negative")
        self._n = n
        checked_edges = []
        for u, v, weight in edges:
            if not 0 <= u < n:
                raise IndexError("u out of range")
            if not 0 <= v < n:
                raise IndexError("v out of range")
            checked_edges.append((u, v, weight))

        dsu_parent = list(range(n))
        dsu_size = [1] * n
        component_node = list(range(n))

        self._parent: list[int | None] = [None] * n
        self._children: list[tuple[int, ...]] = [()] * n
        self._weight: list[int | None] = [None] * n
        self._component_size = [1] * n

        def find(vertex: int) -> int:
            root = vertex
            while dsu_parent[root] != root:
                root = dsu_parent[root]
            while dsu_parent[vertex] != vertex:
                parent = dsu_parent[vertex]
                dsu_parent[vertex] = root
                vertex = parent
            return root

        for u, v, weight in sorted(checked_edges, key=lambda edge: edge[2]):
            root_u = find(u)
            root_v = find(v)
            if root_u == root_v:
                continue

            left = component_node[root_u]
            right = component_node[root_v]
            node = len(self._parent)
            self._parent.append(None)
            self._children.append((left, right))
            self._weight.append(weight)
            self._component_size.append(
                self._component_size[left] + self._component_size[right]
            )
            self._parent[left] = node
            self._parent[right] = node

            if dsu_size[root_u] < dsu_size[root_v]:
                root_u, root_v = root_v, root_u
            dsu_parent[root_v] = root_u
            dsu_size[root_u] += dsu_size[root_v]
            component_node[root_u] = node

        self._roots = [
            node for node, parent in enumerate(self._parent) if parent is None
        ]
        self._depth = [0] * len(self._parent)
        self._tree_root = [-1] * len(self._parent)
        for root in self._roots:
            self._tree_root[root] = root
            stack = [root]
            while stack:
                node = stack.pop()
                for child in self._children[node]:
                    self._depth[child] = self._depth[node] + 1
                    self._tree_root[child] = root
                    stack.append(child)

        levels = max(1, len(self._parent).bit_length())
        first = [
            node if parent is None else parent
            for node, parent in enumerate(self._parent)
        ]
        self._up = [first]
        for _ in range(1, levels):
            previous = self._up[-1]
            self._up.append([previous[previous[node]] for node in range(len(previous))])

    def _validate_node(self, node: int) -> None:
        if not 0 <= node < len(self._parent):
            raise IndexError("node out of range")

    def num_vertices(self) -> int:
        """元グラフの頂点数を返す。"""
        return self._n

    def num_nodes(self) -> int:
        """元頂点と併合ノードを合わせた再構成森のノード数を返す。"""
        return len(self._parent)

    def roots(self) -> list[int]:
        """各連結成分に対応する根を昇順の新しいリストで返す。"""
        return self._roots.copy()

    def parent(self, node: int) -> int | None:
        """``node`` の親を返す。根なら ``None``。"""
        self._validate_node(node)
        return self._parent[node]

    def children(self, node: int) -> tuple[int, ...]:
        """``node`` の子を返す。元頂点なら空tuple。"""
        self._validate_node(node)
        return self._children[node]

    def weight(self, node: int) -> int | None:
        """併合ノードの辺重みを返す。元頂点なら ``None``。"""
        self._validate_node(node)
        return self._weight[node]

    def component_size(self, node: int) -> int:
        """``node`` の部分木に含まれる元頂点数を返す。"""
        self._validate_node(node)
        return self._component_size[node]

    def lca(self, x: int, y: int) -> int | None:
        """再構成森における最小共通祖先を返す。別の木なら ``None``。"""
        self._validate_node(x)
        self._validate_node(y)
        if self._tree_root[x] != self._tree_root[y]:
            return None
        if self._depth[x] < self._depth[y]:
            x, y = y, x
        difference = self._depth[x] - self._depth[y]
        for level in range(len(self._up)):
            if difference >> level & 1:
                x = self._up[level][x]
        if x == y:
            return x
        for level in range(len(self._up) - 1, -1, -1):
            if self._up[level][x] != self._up[level][y]:
                x = self._up[level][x]
                y = self._up[level][y]
        return self._up[0][x]

    def connection_weight(self, u: int, v: int) -> int | None:
        """元頂点 ``u, v`` が初めて連結される辺重みを返す。

        同じ頂点、または元グラフで非連結なら ``None`` を返す。
        """
        if not 0 <= u < self._n:
            raise IndexError("u out of range")
        if not 0 <= v < self._n:
            raise IndexError("v out of range")
        ancestor = self.lca(u, v)
        if ancestor is None or ancestor == u:
            return None
        return self._weight[ancestor]


__all__ = ["KruskalReconstructionTree"]
