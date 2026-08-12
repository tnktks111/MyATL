SegTree
=======

1点更新とモノイドの半開区間積を処理します。使い分けと例は
:doc:`../guides/range_queries` を参照してください。

使いどころ
----------

次の条件に当てはまる問題で使います。

* 配列の1要素を置き換えながら、区間和・最小値・最大値・GCDなどを求める。
* 文字列連結や行列積など、左から右への順序が重要な非可換演算を扱う。
* ``max_right`` / ``min_left`` で「条件を満たす最長区間」を探す。

区間全体への更新が必要なら :class:`lazy_seg_tree.LazySegTree`、1点加算と
区間和だけならコード量が少ない :class:`fenwick.FenwickTree` を選びます。
減算や平均のように結合則を満たさない演算は ``op`` にできません。

区間和の完全例
--------------

区間和を管理する例です。``op`` に加算、``e`` に加算の単位元0を渡します。

.. testcode:: seg-tree-sum

   from seg_tree import SegTree

   values = [2, 1, 3, 2, 4]
   seg = SegTree(lambda left, right: left + right, 0, values)

   assert seg.prod(1, 4) == 6
   assert seg.prod(2, 2) == 0  # 空区間は単位元
   assert seg.get(2) == 3

   seg.set(2, 10)
   assert seg.get(2) == 10
   assert seg.all_prod() == 19

   print(seg.prod(1, 4))
   print(seg.all_prod())

.. testoutput:: seg-tree-sum

   13
   19

空区間 ``prod(left, left)`` は単位元を返します。初期列の代わりに長さを渡すと、
全要素が単位元の木を作れます。

非可換演算
----------

左右の集約順を保つため、文字列連結のような非可換演算にも使えます。

.. testcode:: seg-tree-noncommutative

   from seg_tree import SegTree

   seg = SegTree(lambda left, right: left + right, "", list("abcdef"))
   assert seg.prod(1, 5) == "bcde"

   seg.set(2, "X")
   assert seg.all_prod() == "abXdef"

   print(seg.prod(1, 5))

.. testoutput:: seg-tree-noncommutative

   bXde

代表的なモノイド
----------------

区間最小値・最大値・GCDは、演算と単位元を差し替えるだけです。

.. testcode:: seg-tree-monoids

   from math import gcd
   from seg_tree import SegTree

   values = [12, 18, 6, 15]

   range_min = SegTree(min, float("inf"), values)
   range_max = SegTree(max, -float("inf"), values)
   range_gcd = SegTree(gcd, 0, values)

   assert range_min.prod(1, 4) == 6
   assert range_max.prod(0, 3) == 18
   assert range_gcd.prod(0, 4) == 3

境界探索
--------

要素が非負の区間和なら、先頭 ``left`` から和が ``limit`` 以下である最大の
``right`` を探せます。

.. testcode:: seg-tree-boundary

   from seg_tree import SegTree

   values = [2, 1, 3, 2, 4]
   seg = SegTree(lambda left, right: left + right, 0, values)

   right = seg.max_right(0, lambda total: total <= 6)
   left = seg.min_left(5, lambda total: total <= 6)

   assert right == 3  # sum(values[0:3]) == 6
   assert left == 3   # sum(values[3:5]) == 6
   assert seg.max_right(len(values), lambda total: total == 0) == len(values)
   assert seg.min_left(0, lambda total: total == 0) == 0

   print(left, right)

.. testoutput:: seg-tree-boundary

   3 3

判定関数は単位元に対して真で、探索方向に単調でなければなりません。負数を含む
区間和では一般に単調性が崩れるため、この使い方はできません。

API仕様
-------

.. currentmodule:: seg_tree

.. autoclass:: SegTree
   :members:
   :member-order: bysource
   :show-inheritance:

.. seealso::

   :class:`lazy_seg_tree.LazySegTree` — 区間更新も必要な場合。
