"""
有向グラフの強連結成分分解
（SCC: Strongly Connected Components）。

Tarjanのアルゴリズムを用いて、有向グラフを強連結成分に分解する。
同じ強連結成分に属する任意の2頂点は、互いに到達可能である。

さらに、各強連結成分を1頂点にまとめた縮約グラフを構築できる。
縮約グラフは必ずDAG（有向非巡回グラフ）になる。

頂点番号は 0 以上 N 未満とする。
自己ループおよび多重辺を含むグラフにも対応している。

計算量:
    強連結成分分解:
        O(N + M)

    縮約グラフの構築:
        期待 O(N + M)

空間計算量:
    O(N + M)

主なメソッド:
    add_edge(u, v):
        頂点 u から頂点 v への有向辺を追加する。

    scc_ids():
        次の2つを返す。

        ・強連結成分の個数
        ・各頂点が属する強連結成分の番号

    scc():
        強連結成分ごとの頂点リストを返す。

    condensation_graph():
        各強連結成分を1頂点に縮約したDAGを構築し、
        次の4つを返す。

        ・各強連結成分に属する元の頂点
        ・縮約DAGの隣接リスト
        ・縮約DAGにおける各頂点の入次数
        ・各元頂点が属する強連結成分の番号

成分番号について:
    scc_ids() が返す成分番号、および scc() が返す成分は、
    縮約グラフのトポロジカル順に並んでいる。

    したがって、異なる強連結成分を結ぶ辺 u -> v に対して、

        component_id[u] < component_id[v]

    が成り立つ。

    このため、縮約DAGを順方向に処理する場合は、

        for component in range(group_count):
            ...

    逆トポロジカル順に処理する場合は、

        for component in reversed(range(group_count)):
            ...

    とすればよい。

使用例:
    graph = SCCGraph(6)

    graph.add_edge(0, 1)
    graph.add_edge(1, 0)
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    graph.add_edge(3, 2)
    graph.add_edge(3, 4)
    graph.add_edge(4, 5)
    graph.add_edge(5, 4)

強連結成分のみを取得する場合:
    groups = graph.scc()
    print(groups)

出力:
    [[0, 1], [2, 3], [4, 5]]

各頂点の成分番号を取得する場合:
    group_count, component_id = graph.scc_ids()

    print(group_count)
    print(component_id)

出力:
    3
    [0, 0, 1, 1, 2, 2]

縮約グラフを取得する場合:
    groups, dag, indegree, component_id = (
        graph.condensation_graph()
    )

    print(groups)
    print(dag)
    print(indegree)
    print(component_id)

出力:
    [[0, 1], [2, 3], [4, 5]]
    [[1], [2], []]
    [0, 1, 1]
    [0, 0, 1, 1, 2, 2]

このとき縮約グラフは、

    SCC 0 -> SCC 1 -> SCC 2

となる。

dag[c] が保持するのは、SCC c から辺が直接伸びているSCCのみである。
SCC c から到達可能なすべてのSCCを求める場合は、
縮約DAG上でDFS、BFS、またはDPを行う必要がある。

縮約グラフを構築するとき、同じSCC間に存在する複数の辺は
1本にまとめられ、SCC内部の辺は除外される。

Reference:
    R. Tarjan,
    "Depth-First Search and Linear Graph Algorithms",
    SIAM Journal on Computing, 1972.
"""

import sys
import typing


class CSR:
    def __init__(
            self, n: int, edges: typing.List[typing.Tuple[int, int]]) -> None:
        self.start = [0] * (n + 1)
        self.elist = [0] * len(edges)

        for e in edges:
            self.start[e[0] + 1] += 1

        for i in range(1, n + 1):
            self.start[i] += self.start[i - 1]

        counter = self.start.copy()
        for e in edges:
            self.elist[counter[e[0]]] = e[1]
            counter[e[0]] += 1


class SCCGraph:
    '''
    Reference:
    R. Tarjan,
    Depth-First Search and Linear Graph Algorithms
    '''

    def __init__(self, n: int) -> None:
        self._n = n
        self._edges: typing.List[typing.Tuple[int, int]] = []

    def num_vertices(self) -> int:
        return self._n

    def add_edge(self, from_vertex: int, to_vertex: int) -> None:
        self._edges.append((from_vertex, to_vertex))

    def scc_ids(self) -> typing.Tuple[int, typing.List[int]]:
        g = CSR(self._n, self._edges)
        now_ord = 0
        group_num = 0
        visited = []
        low = [0] * self._n
        order = [-1] * self._n
        ids = [0] * self._n

        sys.setrecursionlimit(max(self._n + 1000, sys.getrecursionlimit()))

        def dfs(v: int) -> None:
            nonlocal now_ord
            nonlocal group_num
            nonlocal visited
            nonlocal low
            nonlocal order
            nonlocal ids

            low[v] = now_ord
            order[v] = now_ord
            now_ord += 1
            visited.append(v)
            for i in range(g.start[v], g.start[v + 1]):
                to = g.elist[i]
                if order[to] == -1:
                    dfs(to)
                    low[v] = min(low[v], low[to])
                else:
                    low[v] = min(low[v], order[to])

            if low[v] == order[v]:
                while True:
                    u = visited[-1]
                    visited.pop()
                    order[u] = self._n
                    ids[u] = group_num
                    if u == v:
                        break
                group_num += 1

        for i in range(self._n):
            if order[i] == -1:
                dfs(i)

        for i in range(self._n):
            ids[i] = group_num - 1 - ids[i]

        return group_num, ids

    def scc(self) -> typing.List[typing.List[int]]:
        ids = self.scc_ids()
        group_num = ids[0]
        counts = [0] * group_num
        for x in ids[1]:
            counts[x] += 1
        groups: typing.List[typing.List[int]] = [[] for _ in range(group_num)]
        for i in range(self._n):
            groups[ids[1][i]].append(i)

        return groups
    
    
    def condensation_graph(
        self,
    ) -> typing.Tuple[
        typing.List[typing.List[int]],  # 各SCCに属する頂点
        typing.List[typing.List[int]],  # 縮約DAGの隣接リスト
        typing.List[int],               # 各SCCの入次数
        typing.List[int],               # 各頂点のSCC番号
    ]:
        group_num, ids = self.scc_ids()

        groups: typing.List[typing.List[int]] = [
            [] for _ in range(group_num)
        ]

        for v in range(self._n):
            groups[ids[v]].append(v)

        dag_set: typing.List[typing.Set[int]] = [
            set() for _ in range(group_num)
        ]

        for u, v in self._edges:
            component_u = ids[u]
            component_v = ids[v]

            if component_u != component_v:
                dag_set[component_u].add(component_v)

        dag = [list(neighbors) for neighbors in dag_set]

        indegree = [0] * group_num

        for component_u in range(group_num):
            for component_v in dag[component_u]:
                indegree[component_v] += 1

        return groups, dag, indegree, ids