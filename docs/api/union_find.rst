UnionFind
=========

無向グラフの連結性を逐次管理します。使い分けと例は
:doc:`../guides/union_find` を参照してください。

使いどころ
----------

無向辺を追加しながら連結判定、成分サイズ、成分数を求める問題に使います。
辺の削除や過去状態への巻き戻しは扱えません。

完全例
------

初期化、併合、連結判定、成分サイズ、成分数、全成分の列挙を含む例です。

.. testcode:: union-find-complete

   from union_find import UnionFind

   union_find = UnionFind(6)

   assert union_find.union(0, 2)
   assert union_find.union(2, 4)
   assert union_find.union(1, 3)

   assert union_find.same(0, 4)
   assert not union_find.same(0, 1)
   assert union_find.size(0) == 3
   assert union_find.group_count() == 3

   # すでに同じ成分なので、状態は変化しない。
   assert not union_find.union(0, 4)

   representative = union_find.find(4)
   groups = union_find.groups()

   print(representative)
   print(groups)

.. testoutput:: union-find-complete

   0
   [[0, 2, 4], [1, 3], [5]]

API仕様
-------

.. currentmodule:: union_find

.. autoclass:: UnionFind
   :members:
   :member-order: bysource
   :show-inheritance:

.. seealso::

   :class:`modified_union_find.weighted_union_find.WeightedUnionFind` —
   ポテンシャル差も必要な場合。
