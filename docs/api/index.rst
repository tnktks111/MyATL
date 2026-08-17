APIリファレンス
===============

API仕様の正本は各ソースファイルのdocstringです。以下の実装名から個別ページへ
移動できます。添字は0-indexed、区間は原則として半開区間
``[left, right)`` です。

.. list-table::
   :header-rows: 1
   :widths: 28 42 30

   * - 実装
     - 主な用途
     - 主な操作
   * - :doc:`union_find`
     - 無向グラフの連結性
     - ``union``, ``same``, ``size``
   * - :doc:`weighted_union_find`
     - 加法ポテンシャル差
     - ``union``, ``diff``
   * - :doc:`graph_union_find`
     - 成分ごとの辺数・閉路・頂点重み
     - ``add_edge``, ``groups``, ``info``
   * - :doc:`successor_dsu`
     - 削除後の次の生存位置
     - ``erase``, ``next``
   * - :doc:`fenwick`
     - 1点加算と区間和
     - ``add``, ``sum``
   * - :doc:`seg_tree`
     - 1点更新と一般の区間積
     - ``set``, ``prod``
   * - :doc:`lazy_seg_tree`
     - 区間更新と区間積
     - ``apply``, ``prod``
   * - :doc:`scc`
     - 強連結成分分解
     - ``scc``, ``scc_ids``
   * - :doc:`kruskal_reconstruction_tree`
     - 重み順の連結成分併合過程・minimax距離
     - ``connection_weight``, ``lca``
   * - :doc:`max_flow`
     - 最大流と最小カット
     - ``flow``, ``min_cut``
   * - :doc:`max_flow_lower_bound`
     - 各辺に下限・上限がある循環流・最大流
     - ``add_edge``, ``circulation``, ``flow``
   * - :doc:`trie`
     - 文字列集合
     - ``insert``, ``search``
   * - :doc:`rolling_hash`
     - 部分文字列の高速比較
     - ``get``, ``same``

.. toctree::
   :maxdepth: 1
   :hidden:

   union_find
   weighted_union_find
   graph_union_find
   successor_dsu
   fenwick
   seg_tree
   lazy_seg_tree
   scc
   kruskal_reconstruction_tree
   max_flow
   max_flow_lower_bound
   trie
   rolling_hash
