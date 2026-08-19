やりたいこと早見表
==================

.. list-table::
   :header-rows: 1
   :widths: 34 22 23 21

   * - やりたいこと
     - 選ぶ実装
     - 主な操作
     - 計算量
   * - 無向グラフの連結性を管理したい
     - :class:`union_find.UnionFind`
     - ``union``, ``same``
     - 償却 :math:`O(\alpha(N))`
   * - 標準入力・標準出力を素早く書きたい
     - :doc:`guides/data_io`
     - ``input``, ``readline``, ``join``
     - 入出力サイズに比例
   * - binaryファイルを読み書きしたい
     - :doc:`guides/binary_io`
     - ``bytes``, ``struct``, ``seek``
     - 入出力サイズに比例
   * - 頂点間のポテンシャル差を管理したい
     - :class:`modified_union_find.weighted_union_find.WeightedUnionFind`
     - ``union``, ``diff``
     - 償却 :math:`O(\alpha(N))`
   * - 削除されていない次の位置を探したい
     - :class:`modified_union_find.successor_dsu.SuccessorDSU`
     - ``erase``, ``next``
     - 償却 :math:`O(\alpha(N))`
   * - 1点加算と区間和を処理したい
     - :class:`fenwick.FenwickTree`
     - ``add``, ``sum``
     - :math:`O(\log N)`
   * - 1点更新と一般の区間積を処理したい
     - :class:`seg_tree.SegTree`
     - ``set``, ``prod``
     - :math:`O(\log N)`
   * - 区間更新と区間積を処理したい
     - :class:`lazy_seg_tree.LazySegTree`
     - ``apply``, ``prod``
     - :math:`O(\log N)`
   * - 強連結成分分解をしたい
     - :class:`scc.SCCGraph`
     - ``scc``, ``scc_ids``
     - :math:`O(N+M)`
   * - 重み順の成分併合過程・minimax距離を求めたい
     - :class:`kruskal_reconstruction_tree.KruskalReconstructionTree`
     - ``connection_weight``, ``lca``
     - 構築 :math:`O(M\log M+N\log N)`、取得 :math:`O(\log N)`
   * - 非負辺の単一始点最短路を求めたい
     - :func:`shortest_path.dijkstra`
     - 距離リスト
     - :math:`O((N+M)\log N)`
   * - 負辺を含む単一始点最短路を求めたい
     - :func:`shortest_path.bellman_ford`
     - 距離リスト、負閉路は ``-inf``
     - :math:`O(NM)`
   * - 全点対最短路を求めたい
     - :func:`shortest_path.warshall_floyd`
     - 距離行列
     - :math:`O(N^3)`
   * - 最大流・最小カットを求めたい
     - :class:`max_flow.MFGraph`
     - ``flow``, ``min_cut``
     - :math:`O(N^2M)`
   * - 各辺に下限がある循環流・最大流を求めたい
     - :class:`max_flow.FlowLowerBound`
     - ``circulation``, ``flow``, ``edges``
     - :math:`O(N^2(N+M))`
   * - 文字列集合を管理したい
     - :class:`trie.Trie`
     - ``insert``, ``search``
     - :math:`O(L)`
   * - Python標準の文字列操作を確認したい
     - :doc:`guides/strings`
     - ``split``, ``join``, ``find``, ``strip`` など
     - 多くは文字列長に比例
   * - 部分文字列を高速比較したい
     - :class:`rolling_hash.RollingHash`
     - ``get``, ``same``
     - 構築 :math:`O(N)`、比較 :math:`O(1)`
   * - 密行列を短く計算したい
     - :doc:`guides/numpy_matrix`
     - ``@``, ``matrix_power``, ``solve``
     - 演算と行列サイズによる
   * - n進数・基数を変換したい
     - :doc:`guides/number_bases`
     - ``bin``, ``format``, ``int(text, base)``
     - 桁数に比例
   * - 動的な順序集合・multisetを使いたい
     - :doc:`guides/sorted_containers`
     - ``add``, ``bisect_left``, ``irange``
     - 多くの操作が近似 :math:`O(\log N)`

判断の目安
----------

区間和だけなら定数倍とコード量が小さいFenwick Tree、非可換演算や境界探索が
必要ならSegment Tree、区間更新まで必要ならLazy Segment Treeを選びます。
静的な文字列1本の部分文字列比較はRolling Hash、文字列集合の追加・検索は
Trieです。一般の無向連結性にはUnion-Findを使い、有向グラフの互いに到達可能な
塊を一括計算するときはSCCを使います。NumPyが利用可能で密な行列をまとめて処理
したい場合は :doc:`guides/numpy_matrix` を参照してください。外部ライブラリを利用
でき、動的な順序集合・multiset・key順mappingが必要なら
:doc:`guides/sorted_containers` を参照してください。
