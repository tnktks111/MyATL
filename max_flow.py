"""Dinic 法による有向グラフの Maximum Flow。"""

from typing import NamedTuple, cast


class MFGraph:
    """非負整数容量の最大流と最小カットを管理する。

    頂点は0-indexed。自己ループ・多重辺・容量0の辺を許す。``flow`` は
    現在の残余グラフからこの呼び出しで追加した流量を返すため、同じ始点・
    終点で複数回呼べる。一般グラフでの計算量は :math:`O(N^2M)`、辺追加は
    :math:`O(1)`、``min_cut`` は :math:`O(N+M)`、空間は :math:`O(N+M)`。

    Args:
        n: 頂点数。0も許す。
    """

    class Edge(NamedTuple):
        """公開辺情報 ``(from_vertex, to_vertex, capacity, flow)``。"""

        from_vertex: int
        to_vertex: int
        capacity: int
        flow: int

    class _Edge:
        def __init__(self, to_vertex: int, capacity: int) -> None:
            self.to_vertex = to_vertex
            self.capacity = capacity
            self.reverse: MFGraph._Edge | None = None

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n must be non-negative")
        self._n = n
        self._graph: list[list[MFGraph._Edge]] = [[] for _ in range(n)]
        self._edges: list[MFGraph._Edge] = []

    def add_edge(
        self, from_vertex: int, to_vertex: int, capacity: int
    ) -> int:
        """有向辺を追加し、0始まりの辺番号を返す。"""
        if not 0 <= from_vertex < self._n:
            raise IndexError("from_vertex out of range")
        if not 0 <= to_vertex < self._n:
            raise IndexError("to_vertex out of range")
        if not isinstance(capacity, int) or capacity < 0:
            raise ValueError("capacity must be a non-negative integer")
        edge_id = len(self._edges)
        edge = MFGraph._Edge(to_vertex, capacity)
        reverse = MFGraph._Edge(from_vertex, 0)
        edge.reverse = reverse
        reverse.reverse = edge
        self._graph[from_vertex].append(edge)
        self._graph[to_vertex].append(reverse)
        self._edges.append(edge)
        return edge_id

    def get_edge(self, edge_id: int) -> Edge:
        """辺番号に対応する容量と現在流量のスナップショットを返す。"""
        if not 0 <= edge_id < len(self._edges):
            raise IndexError("edge_id out of range")
        edge = self._edges[edge_id]
        reverse = cast(MFGraph._Edge, edge.reverse)
        return MFGraph.Edge(
            reverse.to_vertex,
            edge.to_vertex,
            edge.capacity + reverse.capacity,
            reverse.capacity,
        )

    def edges(self) -> list[Edge]:
        """追加順の全辺情報のスナップショットを返す。"""
        return [self.get_edge(edge_id) for edge_id in range(len(self._edges))]

    def change_edge(self, edge_id: int, capacity: int, flow: int) -> None:
        """1辺の容量・流量を変更する。

        ``0 <= flow <= capacity`` が必要。グラフ全体の流量保存則は検証しない。
        """
        if not 0 <= edge_id < len(self._edges):
            raise IndexError("edge_id out of range")
        if not (isinstance(capacity, int) and isinstance(flow, int)
                and 0 <= flow <= capacity):
            raise ValueError("require 0 <= flow <= capacity for integers")
        edge = self._edges[edge_id]
        reverse = cast(MFGraph._Edge, edge.reverse)
        edge.capacity = capacity - flow
        reverse.capacity = flow

    def flow(
        self,
        source: int,
        sink: int,
        flow_limit: int | None = None,
    ) -> int:
        """``source`` から ``sink`` へ追加できた流量を返す。"""
        if not 0 <= source < self._n:
            raise IndexError("source out of range")
        if not 0 <= sink < self._n:
            raise IndexError("sink out of range")
        if source == sink:
            raise ValueError("source and sink must differ")
        if flow_limit is None:
            flow_limit = sum(
                edge.capacity for edges in self._graph for edge in edges
            )
        if not isinstance(flow_limit, int) or flow_limit < 0:
            raise ValueError("flow_limit must be a non-negative integer")

        level = [-1] * self._n
        current_edge = [0] * self._n

        def bfs() -> bool:
            level[:] = [-1] * self._n
            level[source] = 0
            queue = [source]
            front = 0
            while front < len(queue):
                vertex = queue[front]
                front += 1
                for edge in self._graph[vertex]:
                    if edge.capacity == 0 or level[edge.to_vertex] != -1:
                        continue
                    level[edge.to_vertex] = level[vertex] + 1
                    if edge.to_vertex == sink:
                        return True
                    queue.append(edge.to_vertex)
            return False

        def send_one(limit: int) -> int:
            # sink から level が1小さい頂点へ、逆辺の残余容量を見て辿る。
            vertex_stack = [sink]
            path: list[MFGraph._Edge] = []
            while vertex_stack:
                vertex = vertex_stack[-1]
                if vertex == source:
                    sent = min(limit, min(edge.capacity for edge in path))
                    for edge in path:
                        edge.capacity -= sent
                        reverse = cast(MFGraph._Edge, edge.reverse)
                        reverse.capacity += sent
                    return sent
                while current_edge[vertex] < len(self._graph[vertex]):
                    reverse_candidate = self._graph[vertex][current_edge[vertex]]
                    forward = cast(MFGraph._Edge, reverse_candidate.reverse)
                    if (level[reverse_candidate.to_vertex] != level[vertex] - 1
                            or forward.capacity == 0):
                        current_edge[vertex] += 1
                        continue
                    vertex_stack.append(reverse_candidate.to_vertex)
                    path.append(forward)
                    break
                else:
                    vertex_stack.pop()
                    if path:
                        path.pop()
                    level[vertex] = self._n
            return 0

        result = 0
        while result < flow_limit and bfs():
            current_edge[:] = [0] * self._n
            while result < flow_limit:
                sent = send_one(flow_limit - result)
                if sent == 0:
                    break
                result += sent
        return result

    def min_cut(self, source: int) -> list[bool]:
        """現在の残余グラフで ``source`` から到達可能な頂点を返す。"""
        if not 0 <= source < self._n:
            raise IndexError("source out of range")
        visited = [False] * self._n
        visited[source] = True
        stack = [source]
        while stack:
            vertex = stack.pop()
            for edge in self._graph[vertex]:
                if edge.capacity > 0 and not visited[edge.to_vertex]:
                    visited[edge.to_vertex] = True
                    stack.append(edge.to_vertex)
        return visited


class FlowLowerBound:
    """各辺に下限・上限がある有向グラフの循環流・最大流を求める。

    各辺の最終流量 ``flow`` は
    ``lower_bound <= flow <= upper_bound`` を満たす。

    下限分をあらかじめ流した後、超始点・超終点を用いて実行可能性を判定する。
    最大流では人工辺 ``sink -> source`` を加えて循環流へ帰着し、実行可能性の
    確認後に通常の最大流を追加する。頂点は0-indexed。自己ループ、多重辺、下限・
    上限がともに0の辺を許す。

    ``circulation`` は全頂点で流量保存則を満たす実行可能循環流を構築する。
    ``flow`` は指定した始点・終点を除く全頂点で流量保存則を満たし、0以上の
    フロー値を最大化する。どちらか一方を1回だけ呼べる。実行可能なフローが存在
    しない場合、``circulation`` は ``False``、``flow`` は ``-1`` を返し、辺の
    最終流量は取得できない。

    変換後の頂点数は :math:`N+2`、辺数は :math:`O(N+M)`。一般グラフでの
    計算量は :class:`MFGraph` と同様に :math:`O(N^2(N+M))`、空間計算量は
    :math:`O(N+M)`。

    Args:
        n: 頂点数。0も許すが、``flow`` には異なる始点・終点が必要。
    """

    class Edge(NamedTuple):
        """公開辺情報 ``(始点, 終点, 下限, 上限, 最終流量)``。"""

        from_vertex: int
        to_vertex: int
        lower_bound: int
        upper_bound: int
        flow: int

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n must be non-negative")
        self._n = n
        self._super_source = n
        self._super_sink = n + 1
        self._graph = MFGraph(n + 2)
        # 下限分だけ流した時点での「流入 - 流出」。
        self._balance = [0] * n
        # (MFGraph内の辺番号, 始点, 終点, 下限, 上限)
        self._edges: list[tuple[int, int, int, int, int]] = []
        self._upper_bound_sum = 0
        self._solved = False
        self._feasible = False

    def add_edge(
        self,
        from_vertex: int,
        to_vertex: int,
        lower_bound: int,
        upper_bound: int,
    ) -> int:
        """流量範囲 ``[lower_bound, upper_bound]`` の辺を追加する。

        追加順の0始まりの辺番号を返す。``circulation`` または ``flow`` の
        呼び出し後には追加できない。計算量は :math:`O(1)`。
        """
        if self._solved:
            raise RuntimeError(
                "cannot add edges after circulation() or flow()"
            )
        if not 0 <= from_vertex < self._n:
            raise IndexError("from_vertex out of range")
        if not 0 <= to_vertex < self._n:
            raise IndexError("to_vertex out of range")
        if not (
            isinstance(lower_bound, int)
            and isinstance(upper_bound, int)
            and 0 <= lower_bound <= upper_bound
        ):
            raise ValueError("require 0 <= lower_bound <= upper_bound")

        graph_edge_id = self._graph.add_edge(
            from_vertex,
            to_vertex,
            upper_bound - lower_bound,
        )
        self._balance[from_vertex] -= lower_bound
        self._balance[to_vertex] += lower_bound

        edge_id = len(self._edges)
        self._edges.append(
            (
                graph_edge_id,
                from_vertex,
                to_vertex,
                lower_bound,
                upper_bound,
            )
        )
        self._upper_bound_sum += upper_bound
        return edge_id

    def _add_balance_edges(self) -> tuple[list[int], int]:
        """超始点・超終点から需給調整辺を追加する。"""
        auxiliary_edge_ids: list[int] = []
        required_flow = 0
        for vertex, balance in enumerate(self._balance):
            if balance > 0:
                # 下限による流入超過分を、元の辺を通じて流出させる。
                edge_id = self._graph.add_edge(
                    self._super_source,
                    vertex,
                    balance,
                )
                auxiliary_edge_ids.append(edge_id)
                required_flow += balance
            elif balance < 0:
                edge_id = self._graph.add_edge(
                    vertex,
                    self._super_sink,
                    -balance,
                )
                auxiliary_edge_ids.append(edge_id)
        return auxiliary_edge_ids, required_flow

    def _disable_edges(self, edge_ids: list[int]) -> None:
        """指定した補助辺を逆残余辺ごと無効化する。"""
        for edge_id in edge_ids:
            self._graph.change_edge(edge_id, 0, 0)

    def circulation(self) -> bool:
        """下限制約を満たす実行可能循環流を構築する。

        存在する場合は ``True``、存在しない場合は ``False`` を返す。成功後は
        ``get_edge`` または ``edges`` で各辺の流量を取得できる。このメソッドと
        ``flow`` のどちらか一方を1回だけ呼べる。
        """
        if self._solved:
            raise RuntimeError(
                "circulation() and flow() can only be called once"
            )
        self._solved = True

        auxiliary_edge_ids, required_flow = self._add_balance_edges()
        sent = self._graph.flow(
            self._super_source,
            self._super_sink,
            required_flow,
        )
        if sent != required_flow:
            return False

        self._disable_edges(auxiliary_edge_ids)
        self._feasible = True
        return True

    def flow(self, source: int, sink: int) -> int:
        """下限制約を満たす最大流量、実行不能なら ``-1`` を返す。

        最大化するフロー値は ``source`` の正味流出量であり、0以上とする。
        ``circulation`` と合わせて1回だけ呼べる。
        """
        if self._solved:
            raise RuntimeError(
                "circulation() and flow() can only be called once"
            )
        if not 0 <= source < self._n:
            raise IndexError("source out of range")
        if not 0 <= sink < self._n:
            raise IndexError("sink out of range")
        if source == sink:
            raise ValueError("source and sink must differ")
        self._solved = True

        # s -> t フローを循環にする人工辺 t -> s。
        return_edge_id = self._graph.add_edge(
            sink,
            source,
            self._upper_bound_sum,
        )
        auxiliary_edge_ids, required_flow = self._add_balance_edges()

        sent = self._graph.flow(
            self._super_source,
            self._super_sink,
            required_flow,
        )
        if sent != required_flow:
            return -1

        initial_flow = self._graph.get_edge(return_edge_id).flow

        # 補助辺は順辺・逆辺の残余容量をともに0にして完全に取り除く。
        self._disable_edges(auxiliary_edge_ids)
        self._graph.change_edge(return_edge_id, 0, 0)

        additional_flow = self._graph.flow(source, sink)
        self._feasible = True
        return initial_flow + additional_flow

    def get_edge(self, edge_id: int) -> Edge:
        """元の辺の上下限と最終流量のスナップショットを返す。"""
        if not self._solved:
            raise RuntimeError("circulation() or flow() has not been called")
        if not self._feasible:
            raise RuntimeError("no feasible flow exists")
        if not 0 <= edge_id < len(self._edges):
            raise IndexError("edge_id out of range")

        (
            graph_edge_id,
            from_vertex,
            to_vertex,
            lower_bound,
            upper_bound,
        ) = self._edges[edge_id]
        transformed_edge = self._graph.get_edge(graph_edge_id)
        return self.Edge(
            from_vertex=from_vertex,
            to_vertex=to_vertex,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            flow=lower_bound + transformed_edge.flow,
        )

    def edges(self) -> list[Edge]:
        """追加順に全辺の最終流量のスナップショットを返す。"""
        return [
            self.get_edge(edge_id)
            for edge_id in range(len(self._edges))
        ]


__all__ = ["MFGraph", "FlowLowerBound"]
