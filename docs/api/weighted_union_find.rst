WeightedUnionFind
=================

頂点間の加法ポテンシャル差を管理します。使い分けと例は
:doc:`../guides/union_find` を参照してください。

使いどころ
----------

``potential[y] - potential[x] = weight`` という制約を追加しながら、2頂点間の差や
矛盾を検出する問題に使います。制約削除や加法で表せない関係は扱えません。

完全例
------

制約追加、差の取得、未連結判定、整合・矛盾制約、成分サイズを含む例です。

.. testcode:: weighted-union-find-complete

   from modified_union_find.weighted_union_find import WeightedUnionFind

   union_find = WeightedUnionFind(4)

   # potential[1] - potential[0] = 5
   assert union_find.union(0, 1, 5)
   # potential[2] - potential[1] = -2
   assert union_find.union(1, 2, -2)

   assert union_find.same(0, 2)
   assert not union_find.same(0, 3)
   assert union_find.find(0) == union_find.find(2)
   assert union_find.diff(0, 2) == 3
   assert union_find.diff(2, 0) == -3
   assert union_find.diff(0, 3) is None
   assert union_find.size(1) == 3

   # 既存の差と整合する制約はTrue、矛盾する制約はFalse。
   assert union_find.union(0, 2, 3)
   assert not union_find.union(0, 2, 4)
   assert union_find.diff(0, 2) == 3

   print(union_find.weight(2) - union_find.weight(0))
   print(union_find.diff(0, 3))

.. testoutput:: weighted-union-find-complete

   3
   None

API仕様
-------

.. currentmodule:: modified_union_find.weighted_union_find

.. autoclass:: WeightedUnionFind
   :members:
   :member-order: bysource
   :show-inheritance:

.. seealso::

   :class:`union_find.UnionFind` — ポテンシャル差が不要な場合。
