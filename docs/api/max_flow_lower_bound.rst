FlowLowerBound
==============

各辺の流量に下限と上限がある有向グラフで、実行可能循環流または最大流を求めます。
通常の最大流との使い分けは :doc:`../guides/graphs` を参照してください。

使いどころ
----------

各辺が ``lower_bound <= flow <= upper_bound`` を満たす必要がある問題に使います。
たとえば「必ず一定量以上を輸送する」「各割当を最低1回は使う」といった制約です。
始点・終点を持たず全頂点で流量保存を課す場合は ``circulation``、指定した始点から
終点への流量を最大化する場合は ``flow`` を使います。

下限がすべて0なら :class:`max_flow.MFGraph` の方が単純で、複数回の ``flow`` や
``min_cut`` も利用できます。この実装は費用、負容量、頂点需要、フロー値の下限指定を
直接は扱いません。また、``circulation`` と ``flow`` のどちらか一方を1回だけ
呼べます。

実行可能循環流の完全例
------------------------

各頂点で流入量と流出量が等しい流量を構築します。

.. testcode:: lower-bound-circulation-complete

   from max_flow import FlowLowerBound

   graph = FlowLowerBound(3)
   graph.add_edge(0, 1, lower_bound=2, upper_bound=4)
   graph.add_edge(1, 2, lower_bound=1, upper_bound=3)
   graph.add_edge(2, 0, lower_bound=2, upper_bound=2)

   assert graph.circulation() is True

   edges = graph.edges()
   balance = [0, 0, 0]
   for edge in edges:
       assert edge.lower_bound <= edge.flow <= edge.upper_bound
       balance[edge.from_vertex] -= edge.flow
       balance[edge.to_vertex] += edge.flow
   assert balance == [0, 0, 0]

   print([edge.flow for edge in edges])

.. testoutput:: lower-bound-circulation-complete

   [2, 2, 2]

下限制約付き最大流の完全例
----------------------------

辺追加、最大流、最終辺流量、下限・上限の検証を含む例です。

.. testcode:: lower-bound-max-flow-complete

   from max_flow import FlowLowerBound

   graph = FlowLowerBound(4)
   edge_ids = [
       graph.add_edge(0, 1, lower_bound=1, upper_bound=3),
       graph.add_edge(0, 2, lower_bound=0, upper_bound=2),
       graph.add_edge(1, 2, lower_bound=0, upper_bound=1),
       graph.add_edge(1, 3, lower_bound=1, upper_bound=2),
       graph.add_edge(2, 3, lower_bound=1, upper_bound=3),
   ]
   assert edge_ids == [0, 1, 2, 3, 4]

   maximum_flow = graph.flow(source=0, sink=3)
   assert maximum_flow == 5

   edges = graph.edges()
   assert graph.get_edge(0) == edges[0]
   for edge in edges:
       assert edge.lower_bound <= edge.flow <= edge.upper_bound

   source_outflow = sum(
       edge.flow
       for edge in edges
       if edge.from_vertex == 0
   )
   assert source_outflow == maximum_flow

   print(maximum_flow)
   for edge in edges:
       print(edge)

.. testoutput:: lower-bound-max-flow-complete

   5
   Edge(from_vertex=0, to_vertex=1, lower_bound=1, upper_bound=3, flow=3)
   Edge(from_vertex=0, to_vertex=2, lower_bound=0, upper_bound=2, flow=2)
   Edge(from_vertex=1, to_vertex=2, lower_bound=0, upper_bound=1, flow=1)
   Edge(from_vertex=1, to_vertex=3, lower_bound=1, upper_bound=2, flow=2)
   Edge(from_vertex=2, to_vertex=3, lower_bound=1, upper_bound=3, flow=3)

実行不能な例
------------

頂点1へ必ず1流入しますが流出辺がないため、流量保存則を満たせません。

.. testcode:: lower-bound-max-flow-infeasible

   from max_flow import FlowLowerBound

   graph = FlowLowerBound(3)
   graph.add_edge(0, 1, lower_bound=1, upper_bound=1)

   assert graph.flow(source=0, sink=2) == -1

実行不能時と呼び出し順
----------------------

``get_edge`` と ``edges`` は成功した ``circulation`` または実行可能な ``flow`` の後
だけ呼べます。両メソッドは相互に排他的で、成功・失敗にかかわらず合計1回限定です。
呼び出し後には辺を追加できません。最大流値0は実行可能を表し、実行不能の ``-1``
とは区別されます。

API仕様
-------

.. currentmodule:: max_flow

.. autoclass:: FlowLowerBound
   :members:
   :exclude-members: Edge
   :member-order: bysource
   :show-inheritance:

辺情報
------

.. autoclass:: max_flow.FlowLowerBound.Edge
   :members:
   :member-order: bysource

.. seealso::

   :class:`max_flow.MFGraph` — すべての下限が0で、通常の最大流を使える場合。
