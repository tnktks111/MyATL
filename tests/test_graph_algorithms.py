"""SCCとMaximum Flowのnaive差分テスト。"""

import random

from max_flow import MFGraph
from scc import SCCGraph


def _reachability(n: int, edges: list[tuple[int, int]]) -> list[list[bool]]:
    reachable = [[u == v for v in range(n)] for u in range(n)]
    for from_vertex, to_vertex in edges:
        reachable[from_vertex][to_vertex] = True
    for middle in range(n):
        for source in range(n):
            if reachable[source][middle]:
                for sink in range(n):
                    reachable[source][sink] |= reachable[middle][sink]
    return reachable


def test_scc_matches_mutual_reachability_and_topological_ids() -> None:
    rng = random.Random(13579)
    for n in range(9):
        for _ in range(60):
            graph = SCCGraph(n)
            edges = []
            for _ in range(rng.randrange(20)):
                if n == 0:
                    break
                edge = rng.randrange(n), rng.randrange(n)
                edges.append(edge)
                graph.add_edge(*edge)
                if rng.randrange(4) == 0:  # 多重辺
                    edges.append(edge)
                    graph.add_edge(*edge)
            count, component_id = graph.scc_ids()
            assert graph.scc_ids() == (count, component_id)  # 複数回呼び出し
            reachable = _reachability(n, edges)
            for u in range(n):
                for v in range(n):
                    assert (component_id[u] == component_id[v]) == (
                        reachable[u][v] and reachable[v][u]
                    )
            for u, v in edges:
                if component_id[u] != component_id[v]:
                    assert component_id[u] < component_id[v]
            groups, dag, indegree, ids_again = graph.condensation_graph()
            assert ids_again == component_id
            assert count == len(groups) == len(dag) == len(indegree)
            assert sum(indegree) == sum(map(len, dag))
            assert all(len(neighbors) == len(set(neighbors)) for neighbors in dag)


def _minimum_cut_capacity(
    n: int, edges: list[tuple[int, int, int]], source: int, sink: int
) -> int:
    best = sum(capacity for _, _, capacity in edges)
    for mask in range(1 << n):
        if not (mask >> source) & 1 or (mask >> sink) & 1:
            continue
        capacity = sum(
            edge_capacity
            for from_vertex, to_vertex, edge_capacity in edges
            if (mask >> from_vertex) & 1 and not (mask >> to_vertex) & 1
        )
        best = min(best, capacity)
    return best


def test_max_flow_matches_all_cut_enumeration() -> None:
    rng = random.Random(24680)
    for n in range(2, 8):
        for _ in range(70):
            graph = MFGraph(n)
            edges = []
            for _ in range(rng.randrange(16)):
                edge = rng.randrange(n), rng.randrange(n), rng.randrange(5)
                edges.append(edge)
                graph.add_edge(*edge)
            expected = _minimum_cut_capacity(n, edges, 0, n - 1)
            first_limit = rng.randrange(expected + 1) if expected else 0
            first = graph.flow(0, n - 1, first_limit)
            second = graph.flow(0, n - 1)
            assert first + second == expected
            assert graph.flow(0, n - 1) == 0
            reachable = graph.min_cut(0)
            assert not reachable[n - 1]
            cut_capacity = sum(
                capacity for (u, v, capacity) in edges
                if reachable[u] and not reachable[v]
            )
            assert cut_capacity == expected


def test_max_flow_edge_snapshots_self_loops_zero_capacity_and_parallel_edges() -> None:
    graph = MFGraph(2)
    loop = graph.add_edge(0, 0, 7)
    zero = graph.add_edge(0, 1, 0)
    first = graph.add_edge(0, 1, 2)
    second = graph.add_edge(0, 1, 3)
    assert graph.flow(0, 1) == 5
    assert graph.get_edge(loop).flow == 0
    assert graph.get_edge(zero).capacity == 0
    assert graph.get_edge(first).flow + graph.get_edge(second).flow == 5
    snapshot = graph.edges()
    graph.change_edge(first, 4, 1)
    assert snapshot[first].capacity == 2
    assert graph.get_edge(first).capacity == 4


def test_scc_long_path_does_not_change_recursion_limit() -> None:
    import sys

    before = sys.getrecursionlimit()
    graph = SCCGraph(3000)
    for vertex in range(2999):
        graph.add_edge(vertex, vertex + 1)
    count, ids = graph.scc_ids()
    assert count == 3000
    assert ids == list(range(3000))
    assert sys.getrecursionlimit() == before
