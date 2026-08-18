"""最短路の参照実装をnaive解と比較する。"""

import random
from math import inf

from shortest_path import bellman_ford, dijkstra, warshall_floyd


def test_shortest_path_basic_and_negative_cycle() -> None:
    edges = [(0, 1, 5), (0, 1, 2), (1, 2, 3), (2, 3, 0)]
    assert dijkstra(5, edges, 0) == [0, 2, 5, 5, inf]
    assert bellman_ford(5, edges + [(2, 1, -1)], 0) == [0, 2, 5, 5, inf]
    assert warshall_floyd(5, edges)[0] == [0, 2, 5, 5, inf]

    negative_edges = [(0, 1, 1), (1, 2, -3), (2, 1, 1), (2, 3, 2)]
    assert bellman_ford(5, negative_edges, 0) == [0, -inf, -inf, -inf, inf]
    all_pairs = warshall_floyd(5, negative_edges)
    assert all_pairs[0][3] == -inf
    assert all_pairs[3][3] == 0
    assert all_pairs[4][4] == 0


def test_shortest_paths_match_floyd_on_nonnegative_random_graphs() -> None:
    rng = random.Random(97531)
    for n in range(1, 9):
        for _ in range(50):
            edges = [
                (rng.randrange(n), rng.randrange(n), rng.randrange(10))
                for _ in range(rng.randrange(20))
            ]
            all_pairs = warshall_floyd(n, edges)
            for source in range(n):
                assert dijkstra(n, edges, source) == all_pairs[source]
                assert bellman_ford(n, edges, source) == all_pairs[source]


def test_shortest_path_validation_and_empty_graph() -> None:
    assert warshall_floyd(0, []) == []
    try:
        dijkstra(2, [(1, 0, -1)], 0)
    except ValueError:
        pass
    else:
        raise AssertionError("Dijkstra must reject negative edges")

    try:
        bellman_ford(0, [], 0)
    except IndexError:
        pass
    else:
        raise AssertionError("an empty graph has no valid source")
