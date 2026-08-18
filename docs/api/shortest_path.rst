Shortest Path（参照実装）
=========================

問題を解くときにコピー・改変するための、最短路3方式の標準形です。共通APIを
構築することより、緩和処理や負閉路判定の流れをソースで確認しやすいことを優先
しています。辺は ``(from_vertex, to_vertex, weight)`` の有向辺です。

Dijkstra法
-----------

.. testcode:: dijkstra-complete

   from math import inf
   from shortest_path import dijkstra

   edges = [(0, 1, 2), (0, 2, 10), (1, 2, 3), (2, 3, 1)]
   distance = dijkstra(5, edges, source=0)
   assert distance == [0, 2, 5, 6, inf]

非負辺の単一始点最短路です。負辺が1本でもあれば ``ValueError`` になります。

Bellman--Ford法
---------------

.. testcode:: bellman-ford-complete

   from math import inf
   from shortest_path import bellman_ford

   edges = [(0, 1, 4), (1, 2, -2), (2, 3, 1)]
   assert bellman_ford(5, edges, 0) == [0, 4, 2, 3, inf]

   negative_edges = edges + [(3, 1, -1)]
   assert bellman_ford(5, negative_edges, 0) == [0, -inf, -inf, -inf, inf]

負辺を許します。始点から到達可能な負閉路、およびそこから到達可能な頂点は
``-inf`` になります。

Warshall--Floyd法
-----------------

.. testcode:: warshall-floyd-complete

   from math import inf
   from shortest_path import warshall_floyd

   edges = [(0, 1, 3), (0, 2, 10), (1, 2, -1), (2, 3, 4)]
   distance = warshall_floyd(4, edges)
   assert distance[0] == [0, 3, 2, 6]
   assert distance[3] == [inf, inf, inf, 0]

全点対最短路です。負閉路を経由できる頂点対は ``-inf`` になります。

使い分け
--------

.. list-table::
   :header-rows: 1

   * - 関数
     - 条件
     - 計算量
   * - ``dijkstra``
     - 非負辺・単一始点
     - :math:`O((N+M)\log N)`
   * - ``bellman_ford``
     - 負辺を許す・単一始点
     - :math:`O(NM)`
   * - ``warshall_floyd``
     - 全点対
     - :math:`O(N^3)`

API仕様
-------

.. currentmodule:: shortest_path

.. autofunction:: dijkstra
.. autofunction:: bellman_ford
.. autofunction:: warshall_floyd
