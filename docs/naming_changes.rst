命名変更
========

正規名は英語、ファイル・関数・メソッドは ``snake_case``、クラスは
``PascalCase`` に統一しました。

.. list-table:: 公開名・パスの対応表（後方互換なし）
   :header-rows: 1

   * - 変更前
     - 変更後（正規名）
     - 移行上の注意
   * - ``unionfind.py``
     - ``union_find.py``
     - 旧ファイルは削除
   * - ``myUnionFind``
     - ``UnionFind``
     - 旧クラス名は削除
   * - ``get_self_size()``
     - ``size(x)``
     - 旧メソッドは削除
   * - ``Fenwick_Tree``
     - ``FenwickTree``
     - 旧クラス名は削除
   * - ``segtree.py``
     - ``seg_tree.py``
     - 旧ファイルは削除
   * - ``lazysegtree.py``
     - ``lazy_seg_tree.py``
     - 旧ファイルは削除
   * - ``maxflow.py``
     - ``max_flow.py``
     - 旧ファイルは削除
   * - ``rolinghash.py``
     - ``rolling_hash.py``
     - 旧ファイルは削除
   * - ``modified_UF/``
     - ``modified_union_find/``
     - 旧ディレクトリは削除
   * - ``modified_UF/weighted_uf.py``
     - ``modified_union_find/weighted_union_find.py``
     - 旧ファイルは削除
   * - ``Trie.get_all_words_sorted()``
     - ``Trie.words()``
     - 旧メソッドは削除
   * - ``MFGraph.add_edge(src, dst, cap)``
     - ``add_edge(from_vertex, to_vertex, capacity)``
     - 位置引数のみ同じ。旧キーワードは使用不可
   * - ``Edge.src``, ``Edge.dst``, ``Edge.cap``
     - ``from_vertex``, ``to_vertex``, ``capacity``
     - 旧属性は削除
   * - ``MaxFlowLowerBound``
     - ``FlowLowerBound``
     - 循環流と最大流を同じクラスで扱うため改名。旧クラス名は削除

引数名は、区間に ``left, right``、グラフ端点に ``from_vertex, to_vertex``、
要素数・頂点数に ``n``、辺数に説明上 ``m`` を用います。旧ファイル、旧公開名、
旧キーワード引数、内部状態を公開していた属性はいずれも維持していません。
