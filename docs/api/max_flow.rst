MFGraph
=======

非負整数容量の最大流と最小カットを求めます。使い分けと例は
:doc:`../guides/graphs` を参照してください。

使いどころ
----------

容量制約付きネットワーク、二部マッチング、頂点・辺を選ぶ最小カットへの帰着で
使います。費用付き流量、下限制約、浮動小数容量は扱いません。

最大流・最小カットの完全例
--------------------------

辺追加、flow limit、複数回の最大流、辺情報、最小カットを含む例です。

.. testcode:: max-flow-complete

   from max_flow import MFGraph

   graph = MFGraph(4)
   edge_ids = [
       graph.add_edge(0, 1, 2),
       graph.add_edge(0, 2, 1),
       graph.add_edge(1, 2, 1),
       graph.add_edge(1, 3, 1),
       graph.add_edge(2, 3, 2),
   ]
   assert edge_ids == [0, 1, 2, 3, 4]

   # まず2だけ流し、残余グラフから残りを流す。
   assert graph.flow(0, 3, flow_limit=2) == 2
   assert graph.flow(0, 3) == 1
   assert graph.flow(0, 3) == 0

   edges = graph.edges()
   assert graph.get_edge(0) == edges[0]
   assert sum(edge.flow for edge in edges if edge.from_vertex == 0) == 3

   source_side = graph.min_cut(0)
   assert source_side == [True, False, False, False]

   print(sum(edge.flow for edge in edges if edge.from_vertex == 0))
   print(source_side)

.. testoutput:: max-flow-complete

   3
   [True, False, False, False]

``min_cut`` が最小カットを表すのは、最大流を流し切った後です。

辺の変更
--------

``change_edge`` は指定辺の容量と現在流量を直接変更します。グラフ全体の流量保存則は
検証しないため、通常はフローを流す前か、保存則を自分で保証できる場合だけ使います。

.. testcode:: max-flow-change-edge

   from max_flow import MFGraph

   graph = MFGraph(2)
   edge_id = graph.add_edge(0, 1, 10)
   graph.change_edge(edge_id, capacity=12, flow=4)

   edge = graph.get_edge(edge_id)
   assert edge.from_vertex == 0
   assert edge.to_vertex == 1
   assert edge.capacity == 12
   assert edge.flow == 4

   # 順辺には残余容量8がある。
   assert graph.flow(0, 1) == 8

API仕様
-------

.. currentmodule:: max_flow

.. autoclass:: MFGraph
   :members:
   :exclude-members: Edge
   :member-order: bysource
   :show-inheritance:

辺情報
------

.. autoclass:: max_flow.MFGraph.Edge
   :members:
   :member-order: bysource

.. seealso::

   :class:`max_flow.FlowLowerBound` — 各辺に流量の下限がある場合。
