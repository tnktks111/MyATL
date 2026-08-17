KruskalReconstructionTree
==========================

重み付き無向グラフの辺を軽い順に追加したときの、連結成分の併合過程を二分木で
表します。非連結グラフでは複数の根を持つ森になります。

完全例
------

.. testcode:: kruskal-reconstruction-tree-complete

   from kruskal_reconstruction_tree import KruskalReconstructionTree

   tree = KruskalReconstructionTree(
       6,
       [
           (0, 1, 4),
           (1, 2, 2),
           (0, 2, 5),
           (3, 4, -1),
           (2, 3, 7),
       ],
   )

   # 0..5は元頂点、6以降はKruskal法が作った併合ノード。
   assert tree.num_vertices() == 6
   assert tree.num_nodes() == 10
   assert tree.roots() == [5, 9]
   assert tree.children(0) == ()
   assert tree.weight(0) is None
   assert tree.children(6) == (3, 4)
   assert tree.weight(6) == -1
   assert tree.component_size(9) == 5

   # 2頂点が初めて同じ成分になる閾値＝両者間のminimax距離。
   assert tree.connection_weight(1, 2) == 2
   assert tree.connection_weight(0, 2) == 4
   assert tree.connection_weight(0, 4) == 7
   assert tree.connection_weight(0, 5) is None  # 非連結

   ancestor = tree.lca(0, 4)
   assert ancestor is not None
   assert tree.weight(ancestor) == 7
   assert tree.parent(ancestor) is None

注意点
------

``connection_weight(u, v)`` は、重みがその値以下の辺だけを使ったときに ``u`` と
``v`` が初めて連結になる閾値です。同一頂点または非連結な2頂点には ``None`` を
返します。最小全域木そのものの辺一覧、動的な辺追加・削除は扱いません。

API仕様
-------

.. currentmodule:: kruskal_reconstruction_tree

.. autoclass:: KruskalReconstructionTree
   :members:
   :member-order: bysource
   :show-inheritance:
