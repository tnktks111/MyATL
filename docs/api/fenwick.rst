FenwickTree
===========

1点加算と半開区間和を処理します。使い分けと例は
:doc:`../guides/range_queries` を参照してください。

使いどころ
----------

1点加算、区間和、累積頻度からの順位検索が必要な場合に使います。代入更新には現在値
との差を加算します。最小値や非可換演算、区間更新には向きません。

完全例
------

構築、1点加算、空区間・区間和、順位検索を含む例です。

.. testcode:: fenwick-complete

   from fenwick import FenwickTree

   values = [2, 1, 3, 2, 4]
   fenwick = FenwickTree(len(values))
   for index, value in enumerate(values):
       fenwick.add(index, value)

   assert fenwick.sum(1, 4) == 6
   assert fenwick.sum(2, 2) == 0

   fenwick.add(2, 5)
   values[2] += 5
   assert fenwick.sum(0, 3) == sum(values[0:3]) == 11

   # 累積和は [2, 3, 11, 13, 17]。
   assert fenwick.lower_bound(4) == 2
   assert fenwick.lower_bound(18) == len(values)
   assert fenwick.upper_bound(3) == 2
   assert fenwick.upper_bound(17) == len(values)

   print(fenwick.sum(0, len(values)))
   print(fenwick.lower_bound(4), fenwick.upper_bound(3))

.. testoutput:: fenwick-complete

   17
   2 2

``lower_bound`` と ``upper_bound`` は、すべての要素が非負の場合だけ使用できます。

代入更新
--------

Fenwick Treeの更新は加算です。値を代入したい場合は、現在値との差を加えます。

.. testcode:: fenwick-assignment

   from fenwick import FenwickTree

   values = [3, 1, 4]
   fenwick = FenwickTree(len(values))
   for index, value in enumerate(values):
       fenwick.add(index, value)

   index = 1
   new_value = 10
   fenwick.add(index, new_value - values[index])
   values[index] = new_value

   assert fenwick.sum(0, 3) == 17

API仕様
-------

.. currentmodule:: fenwick

.. autoclass:: FenwickTree
   :members:
   :member-order: bysource
   :show-inheritance:

.. seealso::

   :class:`seg_tree.SegTree` — 和以外のモノイドや非可換演算が必要な場合。
