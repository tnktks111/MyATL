LazySegTree
===========

モノイド作用による区間更新と半開区間積を処理します。使い分けと例は
:doc:`../guides/range_queries` を参照してください。

使いどころ
----------

配列の区間をまとめて更新しながら、区間の集約値を求める場合に使います。

.. list-table:: 典型的な設計
   :header-rows: 1
   :widths: 26 27 23 24

   * - やりたいこと
     - ノード値 ``S``
     - 作用 ``F``
     - 合成
   * - 区間加算・区間最小値
     - 最小値
     - 加算値
     - 加算
   * - 区間加算・区間和
     - ``(合計, 長さ)``
     - 加算値
     - 加算
   * - 区間代入・区間和
     - ``(合計, 長さ)``
     - 代入値または恒等作用
     - 新しい代入を優先
   * - 一次関数更新・区間和
     - ``(合計, 長さ)``
     - ``(倍率, 加算値)``
     - 関数合成

区間更新が不要なら :class:`seg_tree.SegTree` の方が設計が単純です。作用が区間の
結合と両立しない場合や、更新後の区間情報をノード値だけから計算できない場合は
この構造をそのまま使えません。

区間加算・区間和の完全例
------------------------

区間和へ加算を反映するには区間長が必要なので、各ノードに ``(合計, 長さ)`` を
保存します。

.. testcode:: lazy-seg-tree-range-add-sum

   from lazy_seg_tree import LazySegTree

   def op(left, right):
       return left[0] + right[0], left[1] + right[1]

   def mapping(addition, node):
       total, length = node
       return total + addition * length, length

   def composition(new, old):
       return new + old

   values = [2, 1, 3, 2, 4]
   initial = [(value, 1) for value in values]
   seg = LazySegTree(
       op=op,
       e=(0, 0),
       mapping=mapping,
       composition=composition,
       identity=0,
       values=initial,
   )

   seg.apply(1, 4, 10)  # values[1:4] に10を加算
   assert seg.prod(1, 4)[0] == 36
   assert seg.get(2)[0] == 13

   seg.apply(0, 5)      # 位置0だけに5を加算
   seg.apply(2, 2, 100) # 空区間なので何もしない
   seg.set(4, (20, 1))  # 位置4を20に置き換える

   assert seg.all_prod()[0] == 63
   print(seg.prod(1, 4)[0])
   print(seg.all_prod()[0])

.. testoutput:: lazy-seg-tree-range-add-sum

   36
   63

``apply(left, right, action)`` は半開区間への更新、``apply(index, action)`` は
1点への更新です。空区間への更新は何もしません。

区間加算・区間最小値
--------------------

区間長が不要な集約では、ノード値を整数のままにできます。

.. testcode:: lazy-seg-tree-range-add-min

   from lazy_seg_tree import LazySegTree

   seg = LazySegTree(
       op=min,
       e=float("inf"),
       mapping=lambda addition, minimum: minimum + addition,
       composition=lambda new, old: new + old,
       identity=0,
       values=[5, 3, 7, 1, 4],
   )

   seg.apply(1, 4, 10)
   assert seg.prod(0, 5) == 4
   assert seg.prod(1, 4) == 11

   seg.apply(4, -5)
   assert seg.all_prod() == -1

区間代入・区間和
----------------

``None`` を恒等作用、整数を代入値とします。新しい代入が古い代入を上書きします。

.. testcode:: lazy-seg-tree-range-assign-sum

   from lazy_seg_tree import LazySegTree

   def op(left, right):
       return left[0] + right[0], left[1] + right[1]

   def mapping(assignment, node):
       total, length = node
       if assignment is None:
           return node
       return assignment * length, length

   def composition(new, old):
       return old if new is None else new

   values = [2, 1, 3, 2, 4]
   seg = LazySegTree(
       op,
       (0, 0),
       mapping,
       composition,
       None,
       [(value, 1) for value in values],
   )

   seg.apply(1, 4, 7)
   assert seg.prod(0, 5)[0] == 27

   seg.apply(2, 5, 0)
   assert seg.all_prod()[0] == 9

区間反転・1の個数
-----------------

0/1配列を反転し、区間内の1の個数を求めます。ノードには1の個数と区間長を持たせます。

.. testcode:: lazy-seg-tree-bit-flip

   from lazy_seg_tree import LazySegTree

   def op(left, right):
       return left[0] + right[0], left[1] + right[1]

   def mapping(flip, node):
       ones, length = node
       return (length - ones, length) if flip else node

   def composition(new, old):
       return new ^ old

   bits = [0, 1, 0, 0, 1]
   seg = LazySegTree(
       op,
       (0, 0),
       mapping,
       composition,
       False,
       [(bit, 1) for bit in bits],
   )

   seg.apply(1, 4, True)
   assert seg.prod(0, 5)[0] == 3

   # 同じ区間をもう一度反転すると元に戻る。
   seg.apply(1, 4, True)
   assert seg.all_prod()[0] == 2

一次関数更新・区間和
--------------------

各要素へ ``x = a*x+b`` を適用します。作用は ``(a, b)`` で表します。

.. testcode:: lazy-seg-tree-affine-sum

   from lazy_seg_tree import LazySegTree

   def op(left, right):
       return left[0] + right[0], left[1] + right[1]

   def mapping(function, node):
       a, b = function
       total, length = node
       return a * total + b * length, length

   def composition(new, old):
       new_a, new_b = new
       old_a, old_b = old
       return new_a * old_a, new_a * old_b + new_b

   seg = LazySegTree(
       op,
       (0, 0),
       mapping,
       composition,
       (1, 0),
       [(value, 1) for value in [1, 2, 3]],
   )

   seg.apply(0, 3, (2, 1))  # 先に x = 2*x+1
   seg.apply(0, 3, (3, 4))  # 次に x = 3*x+4

   assert [seg.get(index)[0] for index in range(3)] == [13, 19, 25]
   assert seg.all_prod()[0] == 57

compositionの順序
-----------------

``composition(new, old)`` は、先に ``old``、その後に ``new`` を適用する作用を
返します。一次関数 ``x -> a*x+b`` では順序を逆にすると結果が変わります。

.. testcode:: lazy-seg-tree-affine-composition

   def compose(new, old):
       new_a, new_b = new
       old_a, old_b = old
       return new_a * old_a, new_a * old_b + new_b

   # 先に 2*x+1、後に 3*x+4 を適用すると 6*x+7。
   assert compose((3, 4), (2, 1)) == (6, 7)

境界探索
--------

``max_right`` と ``min_left`` は、保留中の遅延作用を考慮して境界を探します。

.. testcode:: lazy-seg-tree-boundary

   from lazy_seg_tree import LazySegTree

   def op(left, right):
       return left[0] + right[0], left[1] + right[1]

   def mapping(addition, node):
       total, length = node
       return total + addition * length, length

   seg = LazySegTree(
       op,
       (0, 0),
       mapping,
       lambda new, old: new + old,
       0,
       [(value, 1) for value in [1, 1, 1, 1, 1]],
   )

   seg.apply(1, 4, 2)  # [1, 3, 3, 3, 1]
   assert seg.max_right(0, lambda node: node[0] <= 7) == 3
   assert seg.min_left(5, lambda node: node[0] <= 7) == 2

設計時には次を確認します。

* ``op(e, x) == op(x, e) == x``
* ``mapping(identity, x) == x``
* ``mapping(composition(f, g), x) == mapping(f, mapping(g, x))``
* ``mapping(f, op(x, y)) == op(mapping(f, x), mapping(f, y))``

API仕様
-------

.. currentmodule:: lazy_seg_tree

.. autoclass:: LazySegTree
   :members:
   :member-order: bysource
   :show-inheritance:

.. seealso::

   :class:`seg_tree.SegTree` — 1点更新だけでよい場合。
