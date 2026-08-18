r"""最短路アルゴリズムの参照実装。

問題に合わせてコピー・改変しやすいよう、Dijkstra法、Bellman--Ford法、
Warshall--Floyd法を単純な関数としてまとめる。辺はすべて
``(from_vertex, to_vertex, weight)`` 形式の有向辺で、無向辺は両方向を渡す。
"""

import heapq
from collections import deque
from math import inf

Edge = tuple[int, int, int]
Distance = int | float


def _check_input(n: int, edges: list[Edge]) -> None:
    if n < 0:
        raise ValueError("n must be non-negative")
    for from_vertex, to_vertex, _ in edges:
        if not 0 <= from_vertex < n:
            raise IndexError("from_vertex out of range")
        if not 0 <= to_vertex < n:
            raise IndexError("to_vertex out of range")


def _check_source(n: int, source: int) -> None:
    if not 0 <= source < n:
        raise IndexError("source out of range")


def dijkstra(
    n: int, edges: list[Edge], source: int
) -> tuple[list[Distance], list[int]]:
    r"""非負辺グラフの最短距離 ``dist`` と直前頂点 ``prev`` を返す。

    未到達頂点の距離は ``inf``。計算量は
    :math:`O((N+M)\log N)`、空間は :math:`O(N+M)`。
    """
    _check_input(n, edges)
    _check_source(n, source)
    adj = [[] for _ in range(n)]
    for src, to, w in edges:
        if w < 0:
            raise ValueError("dijkstra requires non-negative edge weights")
        adj[src].append((to, w))

    dist = [inf] * n
    dist[source] = 0
    prev = [-1] * n
    prev[source] = source
    q = [(0, source)]
    while q:
        d, cur = heapq.heappop(q)
        if d != dist[cur]:
            continue
        for nei, w in adj[cur]:
            if d + w < dist[nei]:
                dist[nei] = d + w
                prev[nei] = cur
                heapq.heappush(q, (d + w, nei))
    return dist, prev


def bellman_ford(
    n: int, edges: list[Edge], source: int
) -> tuple[list[Distance], list[int]]:
    r"""負辺を許す最短距離 ``dist`` と直前頂点 ``prev`` を返す。

    未到達頂点は ``inf``。始点から到達可能な負閉路と、そこから到達可能な
    頂点は ``-inf``。計算量は :math:`O(NM)`、空間は :math:`O(N+M)`。
    """
    _check_input(n, edges)
    _check_source(n, source)
    dist = [inf] * n
    dist[source] = 0
    prev = [-1] * n
    prev[source] = source

    # 負閉路がなければ、単純最短路が使う辺は高々N-1本。
    for _ in range(n - 1):
        updated = False
        for src, to, weight in edges:
            if dist[src] == inf:
                continue
            new_distance = dist[src] + weight
            if new_distance < dist[to]:
                dist[to] = new_distance
                prev[to] = src
                updated = True
        if not updated:
            break

    adj = [[] for _ in range(n)]
    affected = [False] * n
    q = deque()
    for src, to, weight in edges:
        adj[src].append(to)
        if (
            dist[src] != inf
            and dist[src] + weight < dist[to]
            and not affected[to]
        ):
            affected[to] = True
            q.append(to)

    # 負閉路から到達できる頂点にも影響を伝播する。
    while q:
        cur = q.popleft()
        for nei in adj[cur]:
            if not affected[nei]:
                affected[nei] = True
                q.append(nei)
    for v in range(n):
        if affected[v]:
            dist[v] = -inf
            prev[v] = -1
    return dist, prev


def warshall_floyd(
    n: int, edges: list[Edge]
) -> tuple[list[list[Distance]], list[list[int]]]:
    r"""全点対最短距離 ``dist`` と次に進む頂点 ``nxt`` を返す。

    未到達な頂点対は ``inf``。負閉路を経由できる頂点対は ``-inf``。
    ``nxt[source][target]`` は最短路で ``source`` の次に進む頂点で、未到達または
    負閉路の影響を受ける場合は ``-1``。
    計算量は :math:`O(N^3)`、空間は :math:`O(N^2)`。
    """
    _check_input(n, edges)
    dist: list[list[Distance]] = [[inf] * n for _ in range(n)]
    nxt = [[-1] * n for _ in range(n)]

    for v in range(n):
        dist[v][v] = 0
        nxt[v][v] = v

    for src, to, w in edges:
        if w < dist[src][to]:
            dist[src][to] = w
            nxt[src][to] = to

    for k in range(n):
        for i in range(n):
            if dist[i][k] == inf:
                continue
            for j in range(n):
                if dist[k][j] == inf:
                    continue
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]

    negative_vertices = [vertex for vertex in range(n) if dist[vertex][vertex] < 0]
    for mid in negative_vertices:
        for src in range(n):
            if dist[src][mid] == inf:
                continue
            for to in range(n):
                if dist[mid][to] != inf:
                    dist[src][to] = -inf
                    nxt[src][to] = -1

    return dist, nxt


def restore_path(
    nxt: list[list[int]], source: int, target: int
) -> list[int] | None:
    """Warshall--Floydの ``nxt`` から ``source`` から ``target`` への経路を返す。

    未到達、または負閉路の影響で最短路が定まらない場合は ``None``。
    """
    n = len(nxt)
    if not 0 <= source < n:
        raise IndexError("source out of range")
    if not 0 <= target < n:
        raise IndexError("target out of range")
    if any(len(row) != n for row in nxt):
        raise ValueError("nxt must be a square matrix")
    if nxt[source][target] == -1:
        return None

    path = [source]
    while source != target:
        source = nxt[source][target]
        path.append(source)
    return path


def restore_path_from_predecessor(
    prev: list[int], source: int, target: int
) -> list[int] | None:
    """DijkstraまたはBellman--Fordの ``prev`` から最短路を復元する。

    未到達、または負閉路の影響で最短路が定まらない場合は ``None``。
    """
    n = len(prev)
    if not 0 <= source < n:
        raise IndexError("source out of range")
    if not 0 <= target < n:
        raise IndexError("target out of range")
    if prev[target] == -1:
        return None

    path = [target]
    while target != source:
        target = prev[target]
        path.append(target)
    path.reverse()
    return path


__all__ = [
    "bellman_ford",
    "dijkstra",
    "restore_path",
    "restore_path_from_predecessor",
    "warshall_floyd",
]
