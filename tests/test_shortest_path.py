"""最短路の参照実装をnaive解と比較する。"""

import random
from math import inf

from shortest_path import (
    bellman_ford,
    dijkstra,
    restore_path,
    restore_path_from_predecessor,
    warshall_floyd,
)


def test_shortest_path_basic_and_negative_cycle() -> None:
    edges = [(0, 1, 5), (0, 1, 2), (1, 2, 3), (2, 3, 0)]
    distance, predecessor = dijkstra(5, edges, 0)
    assert distance == [0, 2, 5, 5, inf]
    assert restore_path_from_predecessor(predecessor, 0, 0) == [0]
    assert restore_path_from_predecessor(predecessor, 0, 3) == [0, 1, 2, 3]
    assert restore_path_from_predecessor(predecessor, 0, 4) is None

    distance, predecessor = bellman_ford(5, edges + [(2, 1, -1)], 0)
    assert distance == [0, 2, 5, 5, inf]
    assert restore_path_from_predecessor(predecessor, 0, 3) == [0, 1, 2, 3]
    distance, next_vertex = warshall_floyd(5, edges)
    assert distance[0] == [0, 2, 5, 5, inf]
    assert restore_path(next_vertex, 0, 0) == [0]
    assert restore_path(next_vertex, 0, 3) == [0, 1, 2, 3]
    assert restore_path(next_vertex, 0, 4) is None

    negative_edges = [(0, 1, 1), (1, 2, -3), (2, 1, 1), (2, 3, 2)]
    distance, predecessor = bellman_ford(5, negative_edges, 0)
    assert distance == [0, -inf, -inf, -inf, inf]
    assert restore_path_from_predecessor(predecessor, 0, 3) is None
    assert restore_path_from_predecessor(predecessor, 0, 0) == [0]
    all_pairs, next_vertex = warshall_floyd(5, negative_edges)
    assert all_pairs[0][3] == -inf
    assert all_pairs[3][3] == 0
    assert all_pairs[4][4] == 0
    assert restore_path(next_vertex, 0, 3) is None
    assert restore_path(next_vertex, 3, 3) == [3]


def test_shortest_paths_match_floyd_on_nonnegative_random_graphs() -> None:
    rng = random.Random(97531)
    for n in range(1, 9):
        for _ in range(50):
            edges = [
                (rng.randrange(n), rng.randrange(n), rng.randrange(10))
                for _ in range(rng.randrange(20))
            ]
            all_pairs, next_vertex = warshall_floyd(n, edges)
            minimum_edges: dict[tuple[int, int], int] = {}
            for u, v, weight in edges:
                minimum_edges[(u, v)] = min(
                    minimum_edges.get((u, v), weight), weight
                )
            for source in range(n):
                dijkstra_distance, dijkstra_predecessor = dijkstra(n, edges, source)
                bellman_distance, bellman_predecessor = bellman_ford(
                    n, edges, source
                )
                assert dijkstra_distance == all_pairs[source]
                assert bellman_distance == all_pairs[source]
                for target in range(n):
                    path = restore_path(next_vertex, source, target)
                    if all_pairs[source][target] == inf:
                        assert path is None
                        continue
                    assert path is not None
                    assert path[0] == source
                    assert path[-1] == target
                    assert sum(
                        minimum_edges[(u, v)] for u, v in zip(path, path[1:])
                    ) == all_pairs[source][target]
                    assert restore_path_from_predecessor(
                        dijkstra_predecessor, source, target
                    ) is not None
                    assert restore_path_from_predecessor(
                        bellman_predecessor, source, target
                    ) is not None


def test_shortest_path_validation_and_empty_graph() -> None:
    assert warshall_floyd(0, []) == ([], [])
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
