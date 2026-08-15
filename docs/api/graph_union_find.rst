GraphUnionFind
==============

辺追加型の無向グラフで、連結成分ごとの頂点数・辺数・閉路・頂点重みを管理します。
使い分けと例は :doc:`../guides/union_find` を参照してください。
コンストラクタには頂点数 ``GraphUnionFind(n)``、または頂点重み列
``GraphUnionFind(weights)`` を渡します。

完全例
------

.. testcode:: graph-union-find-complete

   from modified_union_find.graph_union_find import ComponentInfo, GraphUnionFind

   # 引数が重み列なら、その長さが頂点数になる。
   graph = GraphUnionFind([10, -4, 7, 20, 3])
   assert graph.group_count() == 5
   assert graph.info(0) == ComponentInfo(
       size=1,
       edge_count=0,
       extra_edge_count=0,
       has_cycle=False,
       is_tree=True,
       weight_sum=10,
       weight_max=10,
   )

   # 戻り値Trueは、異なる2成分を併合したことを表す。
   assert graph.add_edge(0, 1)
   assert graph.add_edge(1, 2)
   assert graph.add_edge(3, 4)
   assert graph.group_count() == 2
   assert graph.groups() == [[0, 1, 2], [3, 4]]
   assert graph.same(0, 2)
   assert not graph.same(0, 3)
   assert graph.find(0) == graph.find(2)

   # 頂点0, 1, 2の成分はパスなので木である。
   assert graph.size(1) == 3
   assert graph.edge_count(1) == 2
   assert graph.extra_edge_count(1) == 0
   assert not graph.has_cycle(1)
   assert graph.is_tree(1)
   assert graph.weight_sum(1) == 13
   assert graph.weight_max(1) == 10

   # 同じ成分内に辺を足すとFalseを返し、閉路が1つ増える。
   assert not graph.add_edge(2, 0)
   assert graph.edge_count(1) == 3
   assert graph.extra_edge_count(1) == 1
   assert graph.has_cycle(1)
   assert not graph.is_tree(1)

   # 多重辺も1辺として数え、余分な辺がさらに1本増える。
   assert not graph.add_edge(0, 1)
   assert graph.extra_edge_count(2) == 2

   # 閉路を持つ成分と木を併合しても、余分な辺数は保存される。
   assert graph.add_edge(2, 3)
   assert graph.group_count() == 1
   assert graph.groups() == [[0, 1, 2, 3, 4]]
   assert graph.info(4) == ComponentInfo(
       size=5,
       edge_count=6,
       extra_edge_count=2,
       has_cycle=True,
       is_tree=False,
       weight_sum=36,
       weight_max=20,
   )

   # 自己ループも閉路となる1辺として数える。
   assert not graph.add_edge(4, 4)
   assert graph.edge_count(4) == 7
   assert graph.extra_edge_count(4) == 3

   # 重みが不要なら頂点数を渡す。頂点重みはすべて0になる。
   unweighted_graph = GraphUnionFind(3)
   assert unweighted_graph.add_edge(0, 1)
   assert unweighted_graph.weight_sum(0) == 0
   assert unweighted_graph.weight_max(0) == 0

API仕様
-------

.. currentmodule:: modified_union_find.graph_union_find

.. autoclass:: GraphUnionFind
   :members:
   :member-order: bysource
   :show-inheritance:

.. autoclass:: ComponentInfo
   :members:

.. seealso::

   :class:`union_find.UnionFind` — 連結性と成分サイズだけで十分な場合。
