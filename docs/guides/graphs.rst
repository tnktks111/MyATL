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

:class:`scc.SCCGraph`、:class:`max_flow.MFGraph`、
:class:`max_flow.FlowLowerBound` を参照してください。
