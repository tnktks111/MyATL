SCCGraph
========

有向グラフを強連結成分へ分解します。使い分けと例は
:doc:`../guides/graphs` を参照してください。

使いどころ
----------

有向グラフの閉路をまとめてDAGにしたい場合や、互いに到達可能な頂点を列挙する場合に
使います。辺追加ごとの動的なSCC更新には対応しません。

完全例
------

辺追加、成分番号、成分列挙、縮約DAGと入次数を含む例です。

.. testcode:: scc-complete

   from scc import SCCGraph

   graph = SCCGraph(5)
   edges = [
       (0, 1),
       (1, 0),
       (1, 2),
       (2, 3),
       (3, 2),
       (3, 4),
       (3, 4),  # 多重辺は縮約DAGで1本にまとめられる
       (4, 4),  # 自己ループ
   ]
   for from_vertex, to_vertex in edges:
       graph.add_edge(from_vertex, to_vertex)

   assert graph.num_vertices() == 5

   component_count, component_id = graph.scc_ids()
   assert component_count == 3
   assert component_id == [0, 0, 1, 1, 2]
   assert graph.scc() == [[0, 1], [2, 3], [4]]

   groups, dag, indegree, ids = graph.condensation_graph()
   assert groups == [[0, 1], [2, 3], [4]]
   assert dag == [[1], [2], []]
   assert indegree == [0, 1, 1]
   assert ids == component_id

   print(groups)
   print(dag)

.. testoutput:: scc-complete

   [[0, 1], [2, 3], [4]]
   [[1], [2], []]

成分番号は縮約DAGのトポロジカル順なので、成分間の辺は小さい番号から大きい番号へ
向かいます。

API仕様
-------

.. currentmodule:: scc

.. autoclass:: SCCGraph
   :members:
   :member-order: bysource
   :show-inheritance:
