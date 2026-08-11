"""
有向グラフにおける最大流
（Maximum Flow）。

Dinic法を用いて、始点 s から終点 t へ流せる最大流量を求める。

各有向辺には非負整数の容量を設定する。
内部では、各辺に対応する順辺と逆辺を持つ残余グラフを管理する。

BFSによって始点からの距離を表すレベルグラフを構築し、
レベルグラフ上でDFSを繰り返すことによって
ブロッキングフローを求める。

この実装では再帰によるDFSを使用せず、
終点から始点へ逆向きに探索する反復的なDFSを使用している。

頂点番号は 0 以上 N 未満とする。
自己ループおよび多重辺を含むグラフにも対応している。

計算量:
    一般のグラフにおける最大流:
        O(N^2 M)

    辺の追加:
        1辺あたり O(1)

    最小カットの取得:
        O(N + M)

空間計算量:
    O(N + M)

ここで、Nは頂点数、Mは追加した辺数である。

主なメソッド:
    add_edge(src, dst, cap):
        頂点 src から頂点 dst へ、容量 cap の有向辺を追加する。

        追加した辺の番号を返す。辺番号は0から順に割り当てられる。

    get_edge(i):
        辺番号 i の辺について、次の情報を返す。

        ・始点
        ・終点
        ・容量
        ・現在の流量

    edges():
        追加したすべての辺について、現在の容量と流量を返す。

    change_edge(i, new_cap, new_flow):
        辺番号 i の容量と現在の流量を変更する。

        次の条件を満たす必要がある。

            0 <= new_flow <= new_cap

        このメソッドは、変更後のグラフ全体が流量保存則を満たすかどうかを
        検証しない。

    flow(s, t, flow_limit=None):
        始点 s から終点 t へフローを流し、この呼び出しによって
        新たに追加された流量を返す。

        flow_limitを指定した場合、追加する流量をflow_limit以下に制限する。
        省略した場合は、可能な限りフローを流す。

        同じグラフに対して複数回呼び出した場合、以前のフローを保持した
        状態から追加のフローを計算する。

    min_cut(s):
        現在の残余グラフ上で、頂点 s から到達可能な頂点を求める。

        返されるリストvisitedについて、

            visited[v] == True

        ならば、頂点vは残余グラフ上でsから到達可能である。

        最大流を求めた後に呼び出した場合、Trueとなる頂点集合が
        最小カットの始点側を表す。

辺情報について:
    get_edge()およびedges()が返すEdgeは、次の4つの値を持つ。

        src:
            辺の始点

        dst:
            辺の終点

        cap:
            辺の容量

        flow:
            現在の流量

    内部では、元の容量を直接保持するのではなく、順辺と逆辺の
    残余容量を保持している。

    容量をcap、現在の流量をflowとすると、

        順辺の残余容量 = cap - flow
        逆辺の残余容量 = flow

    となる。

使用例:
    graph = MFGraph(4)

    graph.add_edge(0, 1, 2)
    graph.add_edge(0, 2, 1)
    graph.add_edge(1, 2, 1)
    graph.add_edge(1, 3, 1)
    graph.add_edge(2, 3, 2)

最大流を求める場合:
    max_flow = graph.flow(0, 3)
    print(max_flow)

出力:
    3

各辺の容量と流量を取得する場合:
    for edge in graph.edges():
        print(edge)

出力:
    Edge(src=0, dst=1, cap=2, flow=2)
    Edge(src=0, dst=2, cap=1, flow=1)
    Edge(src=1, dst=2, cap=1, flow=1)
    Edge(src=1, dst=3, cap=1, flow=1)
    Edge(src=2, dst=3, cap=2, flow=2)

辺番号を使って特定の辺を取得する場合:
    edge_id = graph.add_edge(3, 0, 5)
    edge = graph.get_edge(edge_id)
    print(edge)

出力:
    Edge(src=3, dst=0, cap=5, flow=0)

流量に上限を設定する場合:
    limited_graph = MFGraph(2)
    limited_graph.add_edge(0, 1, 10)

    print(limited_graph.flow(0, 1, flow_limit=4))
    print(limited_graph.get_edge(0))

出力:
    4
    Edge(src=0, dst=1, cap=10, flow=4)

再度flow()を呼び出すと、残りの容量に対して追加のフローを計算する。

    print(limited_graph.flow(0, 1))
    print(limited_graph.get_edge(0))

出力:
    6
    Edge(src=0, dst=1, cap=10, flow=10)

最小カットを取得する場合:
    graph = MFGraph(4)

    graph.add_edge(0, 1, 2)
    graph.add_edge(0, 2, 1)
    graph.add_edge(1, 2, 1)
    graph.add_edge(1, 3, 1)
    graph.add_edge(2, 3, 2)

    graph.flow(0, 3)

    reachable = graph.min_cut(0)
    print(reachable)

出力:
    [True, False, False, False]

この場合、最小カットは次の2集合に分かれる。

    始点側:
        {0}

    終点側:
        {1, 2, 3}

始点側から終点側へ伸びる辺、

    0 -> 1
    0 -> 2

の容量の合計は、

    2 + 1 = 3

であり、最大流量と一致する。

注意:
    flow(s, t)が返すのは、グラフに現在流れている総流量ではなく、
    その呼び出しによって新たに追加された流量である。

    例えば、容量10の辺に対して、

        graph.flow(0, 1, flow_limit=4)

    が4を返した後、

        graph.flow(0, 1)

    を呼び出すと、返り値は総流量10ではなく追加流量6となる。

Reference:
Yefim Dinitz,
"Algorithm for Solution of a Problem of Maximum Flow in a Network
with Power Estimation",
Soviet Mathematics Doklady, 1970.
"""

from typing import NamedTuple, Optional, List, cast

class MFGraph:
    class Edge(NamedTuple):
        src: int
        dst: int
        cap: int
        flow: int

    class _Edge:
        def __init__(self, dst: int, cap: int) -> None:
            self.dst = dst
            self.cap = cap
            self.rev: Optional[MFGraph._Edge] = None

    def __init__(self, n: int) -> None:
        self._n = n
        self._g: List[List[MFGraph._Edge]] = [[] for _ in range(n)]
        self._edges: List[MFGraph._Edge] = []

    def add_edge(self, src: int, dst: int, cap: int) -> int:
        assert 0 <= src < self._n
        assert 0 <= dst < self._n
        assert 0 <= cap
        m = len(self._edges)
        e = MFGraph._Edge(dst, cap)
        re = MFGraph._Edge(src, 0)
        e.rev = re
        re.rev = e
        self._g[src].append(e)
        self._g[dst].append(re)
        self._edges.append(e)
        return m

    def get_edge(self, i: int) -> Edge:
        assert 0 <= i < len(self._edges)
        e = self._edges[i]
        re = cast(MFGraph._Edge, e.rev)
        return MFGraph.Edge(
            re.dst,
            e.dst,
            e.cap + re.cap,
            re.cap
        )

    def edges(self) -> List[Edge]:
        return [self.get_edge(i) for i in range(len(self._edges))]

    def change_edge(self, i: int, new_cap: int, new_flow: int) -> None:
        assert 0 <= i < len(self._edges)
        assert 0 <= new_flow <= new_cap
        e = self._edges[i]
        e.cap = new_cap - new_flow
        assert e.rev is not None
        e.rev.cap = new_flow

    def flow(self, s: int, t: int, flow_limit: Optional[int] = None) -> int:
        assert 0 <= s < self._n
        assert 0 <= t < self._n
        assert s != t
        if flow_limit is None:
            flow_limit = cast(int, sum(e.cap for e in self._g[s]))

        current_edge = [0] * self._n
        level = [0] * self._n

        def fill(arr: List[int], value: int) -> None:
            for i in range(len(arr)):
                arr[i] = value

        def bfs() -> bool:
            fill(level, self._n)
            queue = []
            q_front = 0
            queue.append(s)
            level[s] = 0
            while q_front < len(queue):
                v = queue[q_front]
                q_front += 1
                next_level = level[v] + 1
                for e in self._g[v]:
                    if e.cap == 0 or level[e.dst] <= next_level:
                        continue
                    level[e.dst] = next_level
                    if e.dst == t:
                        return True
                    queue.append(e.dst)
            return False

        def dfs(lim: int) -> int:
            stack = []
            edge_stack: List[MFGraph._Edge] = []
            stack.append(t)
            while stack:
                v = stack[-1]
                if v == s:
                    flow = min(lim, min(e.cap for e in edge_stack))
                    for e in edge_stack:
                        e.cap -= flow
                        assert e.rev is not None
                        e.rev.cap += flow
                    return flow
                next_level = level[v] - 1
                while current_edge[v] < len(self._g[v]):
                    e = self._g[v][current_edge[v]]
                    re = cast(MFGraph._Edge, e.rev)
                    if level[e.dst] != next_level or re.cap == 0:
                        current_edge[v] += 1
                        continue
                    stack.append(e.dst)
                    edge_stack.append(re)
                    break
                else:
                    stack.pop()
                    if edge_stack:
                        edge_stack.pop()
                    level[v] = self._n
            return 0

        flow = 0
        while flow < flow_limit:
            if not bfs():
                break
            fill(current_edge, 0)
            while flow < flow_limit:
                f = dfs(flow_limit - flow)
                flow += f
                if f == 0:
                    break
        return flow

    def min_cut(self, s: int) -> List[bool]:
        visited = [False] * self._n
        stack = [s]
        visited[s] = True
        while stack:
            v = stack.pop()
            for e in self._g[v]:
                if e.cap > 0 and not visited[e.dst]:
                    visited[e.dst] = True
                    stack.append(e.dst)
        return visited