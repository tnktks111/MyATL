"""Union-Find 3種の不変条件とnaive差分テスト。"""

import random
from collections import deque

from modified_union_find.graph_union_find import GraphUnionFind
from modified_union_find.successor_dsu import SuccessorDSU
from modified_union_find.weighted_union_find import WeightedUnionFind
from union_find import UnionFind


def test_union_find_handles_empty_singleton_and_duplicate_union() -> None:
    assert UnionFind(0).groups() == []
    union_find = UnionFind(1)
    assert union_find.group_count() == 1
    assert union_find.same(0, 0)
    assert not union_find.union(0, 0)
    assert union_find.size(0) == 1


def test_union_find_matches_naive_component_labels() -> None:
    rng = random.Random(20260811)
    for n in range(1, 15):
        union_find = UnionFind(n)
        label = list(range(n))
        for _ in range(150):
            x = rng.randrange(n)
            y = rng.randrange(n)
            expected_change = label[x] != label[y]
            assert union_find.union(x, y) == expected_change
            if expected_change:
                old, new = label[y], label[x]
                label = [new if value == old else value for value in label]
            for u in range(n):
                for v in range(n):
                    assert union_find.same(u, v) == (label[u] == label[v])
                assert union_find.size(u) == label.count(label[u])
            assert union_find.group_count() == len(set(label))


def test_graph_union_find_tracks_component_information() -> None:
    union_find = GraphUnionFind([10, -4, 7, 20, 3])

    assert union_find.info(0) == (1, 0, 0, False, True, 10, 10)
    assert union_find.add_edge(0, 1)
    assert union_find.add_edge(1, 2)
    assert union_find.info(1) == (3, 2, 0, False, True, 13, 10)
    assert not union_find.add_edge(2, 0)
    assert union_find.info(0) == (3, 3, 1, True, False, 13, 10)

    assert union_find.add_edge(3, 4)
    assert union_find.groups() == [[0, 1, 2], [3, 4]]
    assert union_find.add_edge(2, 3)
    assert union_find.info(4) == (5, 5, 1, True, False, 36, 20)
    assert union_find.group_count() == 1
    assert union_find.groups() == [[0, 1, 2, 3, 4]]


def test_graph_union_find_counts_self_loops_and_parallel_edges() -> None:
    union_find = GraphUnionFind([-5, -2])

    assert not union_find.add_edge(0, 0)
    assert union_find.edge_count(0) == 1
    assert union_find.extra_edge_count(0) == 1
    assert union_find.has_cycle(0)
    assert not union_find.is_tree(0)
    assert union_find.weight_sum(0) == -5
    assert union_find.weight_max(0) == -5

    assert union_find.add_edge(0, 1)
    assert not union_find.add_edge(0, 1)
    assert union_find.size(1) == 2
    assert union_find.edge_count(1) == 3
    assert union_find.extra_edge_count(1) == 2
    assert union_find.weight_sum(1) == -7
    assert union_find.weight_max(1) == -2


def test_graph_union_find_empty_and_index_validation() -> None:
    union_find = GraphUnionFind(0)
    assert union_find.group_count() == 0
    assert union_find.groups() == []
    try:
        union_find.info(0)
    except IndexError:
        pass
    else:
        raise AssertionError("info must reject an out-of-range vertex")


def test_graph_union_find_without_weights_uses_zero() -> None:
    union_find = GraphUnionFind(3)
    assert union_find.add_edge(0, 1)
    assert union_find.info(0) == (2, 1, 0, False, True, 0, 0)
    assert union_find.weight_sum(2) == 0
    assert union_find.weight_max(2) == 0

    try:
        GraphUnionFind(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative n must be rejected")


def _naive_difference(
    graph: list[list[tuple[int, int]]], start: int, goal: int
) -> int | None:
    potential: list[int | None] = [None] * len(graph)
    potential[start] = 0
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        if vertex == goal:
            return potential[vertex]
        for to_vertex, difference in graph[vertex]:
            if potential[to_vertex] is None:
                potential[to_vertex] = potential[vertex] + difference  # type: ignore[operator]
                queue.append(to_vertex)
    return None


def test_weighted_union_find_matches_naive_potential_constraints() -> None:
    rng = random.Random(314159)
    for n in range(1, 12):
        union_find = WeightedUnionFind(n)
        graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]
        for _ in range(180):
            x = rng.randrange(n)
            y = rng.randrange(n)
            weight = rng.randrange(-10, 11)
            known = _naive_difference(graph, x, y)
            expected = known is None or known == weight
            assert union_find.union(x, y, weight) == expected
            if known is None:
                graph[x].append((y, weight))
                graph[y].append((x, -weight))
            for u in range(n):
                for v in range(n):
                    assert union_find.diff(u, v) == _naive_difference(graph, u, v)


def test_weighted_union_find_rejects_contradiction_without_state_change() -> None:
    union_find = WeightedUnionFind(3)
    assert union_find.union(0, 1, 4)
    assert union_find.union(1, 2, -2)
    assert union_find.union(0, 2, 2)
    assert not union_find.union(0, 2, 3)
    assert union_find.diff(0, 2) == 2


def test_successor_dsu_matches_linear_search_and_duplicate_erase() -> None:
    rng = random.Random(271828)
    for n in range(20):
        dsu = SuccessorDSU(n)
        alive = [True] * n
        assert dsu.next(n) == n
        for _ in range(100):
            if n and rng.randrange(2) == 0:
                x = rng.randrange(n)
                assert dsu.erase(x) == alive[x]
                alive[x] = False
            else:
                x = rng.randrange(n + 1)
                expected = next((i for i in range(x, n) if alive[i]), n)
                assert dsu.next(x) == expected


def test_successor_dsu_long_chain_does_not_use_recursion() -> None:
    n = 5000
    dsu = SuccessorDSU(n)
    for x in range(n):
        dsu.erase(x)
    assert dsu.next(0) == n
