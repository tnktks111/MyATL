r"""最短路アルゴリズムの参照実装。

問題に合わせてコピー・改変しやすいよう、Dijkstra法、Bellman--Ford法、
Warshall--Floyd法を単純な関数としてまとめる。辺はすべて
``(from_vertex, to_vertex, weight)`` 形式の有向辺で、無向辺は両方向を渡す。
"""

import heapq
from collections import deque
from collections.abc import Sequence
from math import inf

Edge = tuple[int, int, int]
Distance = int | float


def _check_input(n: int, edges: Sequence[Edge]) -> list[Edge]:
    if n < 0:
        raise ValueError("n must be non-negative")
    checked = list(edges)
    for from_vertex, to_vertex, _ in checked:
        if not 0 <= from_vertex < n:
            raise IndexError("from_vertex out of range")
        if not 0 <= to_vertex < n:
            raise IndexError("to_vertex out of range")
    return checked


def _check_source(n: int, source: int) -> None:
    if not 0 <= source < n:
        raise IndexError("source out of range")


def dijkstra(n: int, edges: Sequence[Edge], source: int) -> list[Distance]:
    r"""非負辺グラフの単一始点最短距離を返す。

    未到達頂点の距離は ``inf``。計算量は
    :math:`O((N+M)\log N)`、空間は :math:`O(N+M)`。
    """
    edges = _check_input(n, edges)
    _check_source(n, source)
    graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for from_vertex, to_vertex, weight in edges:
        if weight < 0:
            raise ValueError("dijkstra requires non-negative edge weights")
        graph[from_vertex].append((to_vertex, weight))

    distance: list[Distance] = [inf] * n
    distance[source] = 0
    priority_queue: list[tuple[Distance, int]] = [(0, source)]
    while priority_queue:
        current_distance, vertex = heapq.heappop(priority_queue)
        if current_distance != distance[vertex]:
            continue
        for to_vertex, weight in graph[vertex]:
            new_distance = current_distance + weight
            if new_distance < distance[to_vertex]:
                distance[to_vertex] = new_distance
                heapq.heappush(priority_queue, (new_distance, to_vertex))
    return distance


def bellman_ford(n: int, edges: Sequence[Edge], source: int) -> list[Distance]:
    r"""負辺を許す単一始点最短距離を返す。

    未到達頂点は ``inf``。始点から到達可能な負閉路と、そこから到達可能な
    頂点は ``-inf``。計算量は :math:`O(NM)`、空間は :math:`O(N+M)`。
    """
    edges = _check_input(n, edges)
    _check_source(n, source)
    distance: list[Distance] = [inf] * n
    distance[source] = 0

    # 負閉路がなければ、単純最短路が使う辺は高々N-1本。
    for _ in range(n - 1):
        updated = False
        for from_vertex, to_vertex, weight in edges:
            if distance[from_vertex] == inf:
                continue
            new_distance = distance[from_vertex] + weight
            if new_distance < distance[to_vertex]:
                distance[to_vertex] = new_distance
                updated = True
        if not updated:
            break

    graph = [[] for _ in range(n)]
    affected = [False] * n
    queue: deque[int] = deque()
    for from_vertex, to_vertex, weight in edges:
        graph[from_vertex].append(to_vertex)
        if (
            distance[from_vertex] != inf
            and distance[from_vertex] + weight < distance[to_vertex]
            and not affected[to_vertex]
        ):
            affected[to_vertex] = True
            queue.append(to_vertex)

    # 負閉路から到達できる頂点にも影響を伝播する。
    while queue:
        vertex = queue.popleft()
        for to_vertex in graph[vertex]:
            if not affected[to_vertex]:
                affected[to_vertex] = True
                queue.append(to_vertex)
    for vertex in range(n):
        if affected[vertex]:
            distance[vertex] = -inf
    return distance


def warshall_floyd(n: int, edges: Sequence[Edge]) -> list[list[Distance]]:
    r"""全点対最短距離を返す。

    未到達な頂点対は ``inf``。負閉路を経由できる頂点対は ``-inf``。
    計算量は :math:`O(N^3)`、空間は :math:`O(N^2)`。
    """
    edges = _check_input(n, edges)
    distance: list[list[Distance]] = [[inf] * n for _ in range(n)]
    for vertex in range(n):
        distance[vertex][vertex] = 0
    for from_vertex, to_vertex, weight in edges:
        distance[from_vertex][to_vertex] = min(
            distance[from_vertex][to_vertex], weight
        )

    for middle in range(n):
        for source in range(n):
            if distance[source][middle] == inf:
                continue
            for target in range(n):
                if distance[middle][target] == inf:
                    continue
                distance[source][target] = min(
                    distance[source][target],
                    distance[source][middle] + distance[middle][target],
                )

    negative_vertices = [vertex for vertex in range(n) if distance[vertex][vertex] < 0]
    for middle in negative_vertices:
        for source in range(n):
            if distance[source][middle] == inf:
                continue
            for target in range(n):
                if distance[middle][target] != inf:
                    distance[source][target] = -inf
    return distance


__all__ = ["bellman_ford", "dijkstra", "warshall_floyd"]
