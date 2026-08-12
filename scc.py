"""有向グラフの Strongly Connected Components (SCC)。"""


class SCCGraph:
    """Kosaraju 法で強連結成分を列挙する有向グラフ。

    頂点は0-indexed。自己ループと多重辺を許す。成分番号は縮約DAGの
    トポロジカル順なので、成分をまたぐ辺 ``u -> v`` について
    ``component_id[u] < component_id[v]`` が成り立つ。

    ``scc_ids`` と ``scc`` は :math:`O(N+M)`、``condensation_graph`` は
    期待 :math:`O(N+M)`、空間は :math:`O(N+M)`。探索は反復実装で、
    Pythonの再帰上限を変更しない。

    Args:
        n: 頂点数。0も許す。
    """

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n must be non-negative")
        self._n = n
        self._edges: list[tuple[int, int]] = []

    def num_vertices(self) -> int:
        """頂点数を返す。"""
        return self._n

    def add_edge(self, from_vertex: int, to_vertex: int) -> None:
        """有向辺 ``from_vertex -> to_vertex`` を追加する。"""
        if not 0 <= from_vertex < self._n:
            raise IndexError("from_vertex out of range")
        if not 0 <= to_vertex < self._n:
            raise IndexError("to_vertex out of range")
        self._edges.append((from_vertex, to_vertex))

    def scc_ids(self) -> tuple[int, list[int]]:
        """``(component_count, component_id)`` を返す。"""
        graph = [[] for _ in range(self._n)]
        reverse_graph = [[] for _ in range(self._n)]
        for from_vertex, to_vertex in self._edges:
            graph[from_vertex].append(to_vertex)
            reverse_graph[to_vertex].append(from_vertex)

        visited = [False] * self._n
        finish_order: list[int] = []
        for start in range(self._n):
            if visited[start]:
                continue
            visited[start] = True
            stack: list[tuple[int, int]] = [(start, 0)]
            while stack:
                vertex, edge_index = stack[-1]
                if edge_index < len(graph[vertex]):
                    to_vertex = graph[vertex][edge_index]
                    stack[-1] = (vertex, edge_index + 1)
                    if not visited[to_vertex]:
                        visited[to_vertex] = True
                        stack.append((to_vertex, 0))
                else:
                    finish_order.append(vertex)
                    stack.pop()

        component_id = [-1] * self._n
        component_count = 0
        for start in reversed(finish_order):
            if component_id[start] != -1:
                continue
            component_id[start] = component_count
            stack = [start]
            while stack:
                vertex = stack.pop()
                for to_vertex in reverse_graph[vertex]:
                    if component_id[to_vertex] == -1:
                        component_id[to_vertex] = component_count
                        stack.append(to_vertex)
            component_count += 1
        return component_count, component_id

    def scc(self) -> list[list[int]]:
        """トポロジカル順に各成分の頂点リストを返す。"""
        component_count, component_id = self.scc_ids()
        groups = [[] for _ in range(component_count)]
        for vertex, group in enumerate(component_id):
            groups[group].append(vertex)
        return groups

    def condensation_graph(
        self,
    ) -> tuple[list[list[int]], list[list[int]], list[int], list[int]]:
        """``(groups, dag, indegree, component_id)`` を返す。

        ``dag`` では成分内辺を除き、成分間の多重辺を1本にまとめる。
        """
        component_count, component_id = self.scc_ids()
        groups = [[] for _ in range(component_count)]
        for vertex, group in enumerate(component_id):
            groups[group].append(vertex)
        dag_sets = [set() for _ in range(component_count)]
        for from_vertex, to_vertex in self._edges:
            source = component_id[from_vertex]
            destination = component_id[to_vertex]
            if source != destination:
                dag_sets[source].add(destination)
        dag = [sorted(neighbors) for neighbors in dag_sets]
        indegree = [0] * component_count
        for neighbors in dag:
            for destination in neighbors:
                indegree[destination] += 1
        return groups, dag, indegree, component_id


__all__ = ["SCCGraph"]
