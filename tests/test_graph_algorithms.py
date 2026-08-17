"""SCCとMaximum Flowのnaive差分テスト。"""

import random

from kruskal_reconstruction_tree import KruskalReconstructionTree
from max_flow import MFGraph
from scc import SCCGraph


def test_kruskal_reconstruction_tree_structure_and_queries() -> None:
    tree = KruskalReconstructionTree(
        6,
        [
            (0, 1, 4),
            (1, 2, 2),
            (0, 2, 5),  # 追加時にはすでに同じ成分なので不採用
            (3, 4, -1),
            (2, 3, 7),
            (0, 0, -10),  # 自己ループ
        ],
    )
    assert tree.num_vertices() == 6
    assert tree.num_nodes() == 10
    assert tree.roots() == [5, 9]
    assert tree.children(0) == ()
    assert tree.weight(0) is None
    assert tree.children(6) == (3, 4)
    assert tree.weight(6) == -1
    assert tree.component_size(9) == 5
    assert tree.parent(9) is None
    assert tree.connection_weight(1, 2) == 2
    assert tree.connection_weight(0, 2) == 4
    assert tree.connection_weight(0, 4) == 7
    assert tree.connection_weight(0, 5) is None
    assert tree.connection_weight(5, 5) is None
    assert tree.weight(tree.lca(0, 4)) == 7  # type: ignore[arg-type]


def test_kruskal_reconstruction_tree_empty_and_validation() -> None:
    tree = KruskalReconstructionTree(0)
    assert tree.num_nodes() == 0
    assert tree.roots() == []
    try:
        KruskalReconstructionTree(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative n must be rejected")

    try:
        KruskalReconstructionTree(2, [(0, 2, 1)])
    except IndexError:
        pass
    else:
        raise AssertionError("out-of-range endpoint must be rejected")


def test_kruskal_reconstruction_tree_deep_tree_root_detection() -> None:
    n = 20
    edges = [(0, vertex, vertex) for vertex in range(1, n - 1)]
    tree = KruskalReconstructionTree(n, edges)
    assert tree.connection_weight(0, n - 2) == n - 2
    assert tree.connection_weight(0, n - 1) is None
    assert tree.lca(0, n - 1) is None


def test_kruskal_reconstruction_tree_matches_minimax_paths() -> None:
    rng = random.Random(86420)
    infinity = 10**9
    for n in range(1, 9):
        for _ in range(50):
            edges = [
                (rng.randrange(n), rng.randrange(n), rng.randrange(-5, 8))
                for _ in range(rng.randrange(18))
            ]
            tree = KruskalReconstructionTree(n, edges)
            minimax = [[infinity] * n for _ in range(n)]
            for u, v, weight in edges:
                if u != v:
                    minimax[u][v] = min(minimax[u][v], weight)
                    minimax[v][u] = min(minimax[v][u], weight)
            for middle in range(n):
                for u in range(n):
                    for v in range(n):
                        minimax[u][v] = min(
                            minimax[u][v], max(minimax[u][middle], minimax[middle][v])
                        )
            for u in range(n):
                assert tree.connection_weight(u, u) is None
                for v in range(u + 1, n):
                    expected = None if minimax[u][v] == infinity else minimax[u][v]
                    assert tree.connection_weight(u, v) == expected


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
