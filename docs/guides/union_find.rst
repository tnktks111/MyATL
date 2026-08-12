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
:class:`modified_union_find.weighted_union_find.WeightedUnionFind`、
:class:`modified_union_find.successor_dsu.SuccessorDSU` を参照してください。
