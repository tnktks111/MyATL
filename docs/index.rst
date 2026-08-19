MyATL: 競技プログラミング用Pythonライブラリ
================================================

MyATLは、試験中に目的の実装を探し、前提・API・計算量を確認して、そのまま
コピーするための小さなライブラリです。全実装はPython標準ライブラリだけで
動きます。添字は0-indexed、区間は原則 ``[left, right)`` です。

最初に :doc:`quick_reference` から目的に合う構造を選んでください。実装を
コピーする前には用途別ガイドの「使えないこと」と注意点も確認してください。

.. toctree::
   :maxdepth: 2
   :caption: 目的から探す

   quick_reference
   guides/data_io
   guides/union_find
   guides/range_queries
   guides/graphs
   guides/strings
   guides/sorted_containers
   guides/numpy_matrix
   guides/number_bases

.. toctree::
   :maxdepth: 2
   :caption: 仕様と品質

   api/index
   audit
   naming_changes

最小動作例
----------

.. testcode:: index-quick-start

   from union_find import UnionFind
   from fenwick import FenwickTree

   union_find = UnionFind(4)
   union_find.union(0, 1)
   assert union_find.same(0, 1)
   assert not union_find.same(0, 2)

   fenwick = FenwickTree(4)
   for index, value in enumerate([2, 1, 3, 4]):
       fenwick.add(index, value)
   assert fenwick.sum(1, 4) == 8

   print(union_find.groups())
   print(fenwick.sum(0, 4))

.. testoutput:: index-quick-start

   [[0, 1], [2], [3]]
   10
