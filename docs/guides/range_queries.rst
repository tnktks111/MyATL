区間クエリガイド
================

Fenwick Tree
------------

1点加算と区間和に最も簡潔です。累積頻度が非負なら ``lower_bound`` と
``upper_bound`` で順位位置も探せます。

.. testcode:: guide-fenwick

   from fenwick import FenwickTree

   bit = FenwickTree(5)
   bit.add(2, 4)
   assert bit.sum(0, 3) == 4

代入更新には現在値との差を加算する必要があります。最小値、非可換演算、区間更新
には向きません。境界探索は負の要素を加えた後には使えません。

Segment Tree
------------

結合則と単位元を持つ任意のモノイドを扱い、文字列連結や行列積のような非可換演算
でも左から右の順序を保ちます。

.. testcode:: guide-seg-tree

   from seg_tree import SegTree

   seg = SegTree(lambda a, b: a + b, "", list("abcd"))
   assert seg.prod(1, 3) == "bc"

逆元は不要ですが、結合的でない減算などは使えません。区間更新が必要なら
Lazy Segment Treeを選びます。``max_right`` / ``min_left`` の述語には単調性と
``f(e) == True`` が必要です。

Lazy Segment Tree
-----------------

区間更新と区間積を両方 :math:`O(\log N)` で行います。区間加算・区間和では
区間情報に長さも含めます。

.. testcode:: guide-lazy-seg-tree

   from lazy_seg_tree import LazySegTree

   op = lambda x, y: (x[0] + y[0], x[1] + y[1])
   mapping = lambda add, x: (x[0] + add * x[1], x[1])
   composition = lambda new, old: new + old
   seg = LazySegTree(op, (0, 0), mapping, composition, 0,
                     [(3, 1), (1, 1), (4, 1)])
   seg.apply(0, 2, 5)
   assert seg.prod(0, 3)[0] == 18

最も多い誤りは ``composition`` の順序です。新しい作用 ``f``、保留済み作用 ``g``
に対し「先にg、後にf」です。作用が区間結合と両立しない更新には使えません。

API仕様
-------

:class:`fenwick.FenwickTree`、:class:`seg_tree.SegTree`、
:class:`lazy_seg_tree.LazySegTree` を参照してください。
