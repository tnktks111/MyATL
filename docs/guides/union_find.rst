Union-Find系ガイド
==================

UnionFind
---------

辺を順次追加する無向グラフで、連結判定・成分サイズ・成分数を管理します。

.. testcode:: guide-union-find

   from union_find import UnionFind

   uf = UnionFind(5)
   uf.union(0, 2)
   assert uf.same(0, 2)
   assert uf.size(0) == 2

辺の削除、連結時刻の巻き戻し、各成分の辺一覧は扱えません。その場合は
offline query、rollback DSU、別途の隣接リストを検討します。

WeightedUnionFind
-----------------

``potential[y] - potential[x] = weight`` という加法制約を追加し、差を求めます。

.. testcode:: guide-weighted-union-find

   from modified_union_find.weighted_union_find import WeightedUnionFind

   uf = WeightedUnionFind(3)
   uf.union(0, 1, 5)
   uf.union(1, 2, -2)
   assert uf.diff(0, 2) == 3

``union`` が ``False`` なら既存制約と矛盾しています。非可換群、制約削除、矛盾後も
全制約を保持して原因を説明する用途には使えません。

GraphUnionFind
--------------

辺を追加しながら、連結成分ごとの辺数、閉路、余分な辺数、頂点重みを管理します。

.. testcode:: guide-graph-union-find

   from modified_union_find.graph_union_find import GraphUnionFind

   graph = GraphUnionFind([10, 20, 30])  # 頂点重みを指定
   graph.add_edge(0, 1)
   graph.add_edge(1, 2)
   assert graph.is_tree(0)
   assert graph.weight_sum(0) == 60
   graph.add_edge(2, 0)
   assert graph.has_cycle(0)
   assert graph.extra_edge_count(0) == 1

重みが不要なら頂点数だけを渡せます。集約される頂点重みは0になります。

.. testcode:: guide-graph-union-find

   unweighted_graph = GraphUnionFind(4)
   unweighted_graph.add_edge(0, 1)
   assert unweighted_graph.weight_sum(0) == 0

自己ループと多重辺も1辺として数えます。辺・頂点の削除、辺重み、頂点重みの変更は
扱えません。

SuccessorDSU
------------

位置を一度だけ削除し、指定位置以降の未削除位置を高速に探します。

.. testcode:: guide-successor-dsu

   from modified_union_find.successor_dsu import SuccessorDSU

   successor = SuccessorDSU(5)
   successor.erase(2)
   assert successor.next(2) == 3

返り値 ``n`` は「存在しない」という番兵です。削除の取り消し、前の生存位置、
任意順序統計量には使えないため、Fenwick Treeや平衡木相当の構造を検討します。

API仕様
-------

:class:`union_find.UnionFind`、
:class:`modified_union_find.graph_union_find.GraphUnionFind`、
:class:`modified_union_find.weighted_union_find.WeightedUnionFind`、
:class:`modified_union_find.successor_dsu.SuccessorDSU` を参照してください。
