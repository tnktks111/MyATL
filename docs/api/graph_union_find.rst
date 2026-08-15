GraphUnionFind
==============

辺追加型の無向グラフで、連結成分ごとの頂点数・辺数・閉路・頂点重みを管理します。
使い分けと例は :doc:`../guides/union_find` を参照してください。

完全例
------

.. testcode:: graph-union-find-complete

   from modified_union_find.graph_union_find import GraphUnionFind

   graph = GraphUnionFind([10, -4, 7])
   graph.add_edge(0, 1)
   graph.add_edge(1, 2)
   assert graph.info(0).is_tree
   assert graph.info(0).weight_sum == 13

   # 同じ成分内の辺なので閉路が1つ増える。
   assert not graph.add_edge(2, 0)
   assert graph.edge_count(1) == 3
   assert graph.extra_edge_count(1) == 1
   assert graph.has_cycle(1)

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
