グラフアルゴリズムガイド
========================

Strongly Connected Components
-----------------------------

有向グラフを、相互に到達可能な頂点の極大集合へ分解します。成分番号は縮約DAGの
トポロジカル順なので、そのまま前からDPできます。

.. testcode:: guide-scc

   from scc import SCCGraph

   graph = SCCGraph(3)
   graph.add_edge(0, 1)
   graph.add_edge(1, 0)
   graph.add_edge(1, 2)
   assert graph.scc() == [[0, 1], [2]]

無向連結性の逐次管理ならUnion-Findの方が簡潔です。SCCは辺追加後の再計算を高速化
する動的構造ではなく、呼ぶたびに :math:`O(N+M)` で全体を計算します。

Kruskal Reconstruction Tree
----------------------------

重み付き無向グラフで、辺を軽い順に追加したときの連結成分の併合過程を木にします。
2頂点が連結になる最小の重み閾値（minimax距離）も取得できます。

.. testcode:: guide-kruskal-reconstruction-tree

   from kruskal_reconstruction_tree import KruskalReconstructionTree

   tree = KruskalReconstructionTree(
       4,
       [(0, 1, 3), (1, 2, 5), (0, 2, 8), (2, 3, 10)],
   )
   assert tree.connection_weight(0, 2) == 5
   assert tree.connection_weight(0, 3) == 10

元頂点は ``0..n-1``、併合ノードは ``n`` 以降です。非連結なら森になり、異なる木の
頂点間では ``connection_weight`` が ``None`` を返します。辺の動的変更には対応
しません。

Shortest Paths
--------------

辺を ``(from_vertex, to_vertex, weight)`` で渡し、条件に応じて3方式を使い分けます。

.. testcode:: guide-shortest-path

   from shortest_path import bellman_ford, dijkstra, warshall_floyd

   edges = [(0, 1, 2), (1, 2, 3), (0, 2, 10)]
   assert dijkstra(3, edges, 0)[2] == 5
   assert bellman_ford(3, edges + [(2, 1, -1)], 0)[2] == 5
   assert warshall_floyd(3, edges)[0][2] == 5

非負辺の単一始点ならDijkstra、負辺を含む単一始点ならBellman--Ford、全点対なら
Warshall--Floydを選びます。未到達は ``inf``、到達可能な負閉路の影響で最短距離が
定まらない場合は ``-inf`` です。結果は距離リストまたは距離行列を直接返します。
無向辺は両方向を追加します。

Maximum Flow / Minimum Cut
--------------------------

非負整数容量の有向ネットワークにDinic法を適用します。

.. testcode:: guide-max-flow

   from max_flow import MFGraph

   graph = MFGraph(4)
   graph.add_edge(0, 1, 2)
   graph.add_edge(0, 2, 1)
   graph.add_edge(1, 3, 2)
   graph.add_edge(2, 3, 1)
   assert graph.flow(0, 3) == 3
   source_side = graph.min_cut(0)
   assert source_side == [True, False, False, False]

``flow`` の返り値は総流量でなく、その呼び出しで増えた量です。``min_cut`` が最小
カットになるのは最大流を流し切った後です。負容量・浮動小数容量・費用付き流量・
下限制約は扱いません。``change_edge`` は流量保存則を自動検証しません。

Lower-Bounded Maximum Flow
--------------------------

各辺に流量の下限がある場合は ``FlowLowerBound`` を使います。始点・終点のない
循環流の実行可能性判定と、始点・終点を指定する最大流の両方に対応します。

.. testcode:: guide-lower-bound-max-flow

   from max_flow import FlowLowerBound

   graph = FlowLowerBound(3)
   graph.add_edge(0, 1, lower_bound=1, upper_bound=3)
   graph.add_edge(1, 2, lower_bound=1, upper_bound=2)
   graph.add_edge(0, 2, lower_bound=0, upper_bound=2)

   assert graph.flow(0, 2) == 4
   assert all(
       edge.lower_bound <= edge.flow <= edge.upper_bound
       for edge in graph.edges()
   )

下限がすべて0なら ``MFGraph`` を使います。下限制約版は ``circulation`` または
``flow`` の片方を1回だけ呼べます。実行可能な最大流がなければ ``-1`` を返します。
最大流値0は実行可能なので区別してください。費用付き流量や下限付き最小費用流には
対応しません。

API仕様
-------

:class:`scc.SCCGraph`、
:class:`kruskal_reconstruction_tree.KruskalReconstructionTree`、
:func:`shortest_path.dijkstra`、:func:`shortest_path.bellman_ford`、
:func:`shortest_path.warshall_floyd`、
:class:`max_flow.MFGraph`、
:class:`max_flow.FlowLowerBound` を参照してください。
