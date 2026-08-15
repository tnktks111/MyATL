Sorted Containersガイド
=======================

``sortedcontainers`` 2.4系で、要素を追加・削除しながらソート順、順位、境界探索を
利用するためのガイドです。pure Pythonの外部ライブラリなので、使用前に試験環境へ
導入済みか確認してください。

.. code-block:: console

   python -m pip install "sortedcontainers>=2.4,<3"

選び方
------

.. list-table::
   :header-rows: 1
   :widths: 23 32 24 21

   * - 構造
     - 選ぶ状況
     - 重複
     - 主な特徴
   * - ``SortedList``
     - multiset、中央値、順位、前後要素
     - 保持する
     - 値順とindexの両方
   * - ``SortedKeyList``
     - objectを抽出key順で保持
     - 値もkeyも重複可
     - ``key=`` による順序
   * - ``SortedSet``
     - 集合判定とソート順を両立
     - 除去する
     - set演算と順位アクセス
   * - ``SortedDict``
     - key-valueをkey順で保持
     - keyは一意
     - mappingとkeyの境界探索

値の更新がなく最初に1回ソートするだけなら組み込み ``sorted``、挿入が少ないなら
``bisect`` とlist、最小値だけを取り出すなら ``heapq`` の方が依存もコードも小さく
なります。値域を事前に座標圧縮でき、個数やprefix sumを管理したい場合はFenwick Tree
も候補です。

計算量の読み方
--------------

このページの「近似 :math:`O(\log N)`」は、公式APIドキュメントの
``O(log(n)) -- approximate`` に対応します。内部は平衡二分探索木ではなく、既定の
load factorを持つ二段のlist-of-listsです。binary searchに加えて短いsublist内の
要素移動があるため、厳密な最悪計算量 :math:`O(\log N)` を要求する証明には使えません。
通常の競技用途ではAPI記載の近似計算量を選択の目安とし、厳密保証が必要なら問題に
適した別実装を使います。

以下で :math:`N` は格納要素数、:math:`K` は追加数または出力要素数です。iteratorを
返す範囲操作には、境界探索に加えて実際に列挙した :math:`K` 個分の時間が必要です。

SortedList
----------

重複を保持する、常に昇順のmutable sequenceです。multisetとして使え、0-indexedの
順位アクセスと負のindexを利用できます。

完全例
^^^^^^

.. testcode:: sorted-list-complete

   from sortedcontainers import SortedList

   values = SortedList([5, 1, 3, 3, 8])
   values.add(2)
   assert list(values) == [1, 2, 3, 3, 5, 8]

   # 3未満の個数、3以下の個数、3の個数。
   assert values.bisect_left(3) == 2
   assert values.bisect_right(3) == 4
   assert values.count(3) == 2

   target = 4
   predecessor_index = values.bisect_right(target) - 1
   successor_index = values.bisect_left(target)
   predecessor = (
       values[predecessor_index]
       if predecessor_index >= 0
       else None
   )
   successor = (
       values[successor_index]
       if successor_index < len(values)
       else None
   )
   assert (predecessor, successor) == (3, 5)

   # 値の範囲はinclusiveを指定。indexの範囲は[left, right)。
   assert list(
       values.irange(2, 5, inclusive=(True, False))
   ) == [2, 3, 3]
   assert list(values.islice(1, 4)) == [2, 3, 3]

   values.remove(3)    # 1個だけ削除。なければValueError。
   values.discard(99)  # なければ何もしない。
   minimum = values.pop(0)

   assert minimum == 1
   print(list(values))

.. testoutput:: sorted-list-complete

   [2, 3, 5, 8]

主要APIと計算量
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 34 39 27

   * - API
     - 動作
     - 計算量
   * - ``SortedList(iterable)``
     - 初期値をソートして構築
     - :math:`O(N\log N)`
   * - ``len(values)``
     - 要素数
     - :math:`O(1)`
   * - ``add(value)``
     - 1要素追加
     - 近似 :math:`O(\log N)`
   * - ``update(iterable)``
     - :math:`K` 要素追加
     - 近似 :math:`O(K\log N)`
   * - ``discard(value)``
     - 存在すれば1個削除
     - 近似 :math:`O(\log N)`
   * - ``remove(value)``
     - 1個削除。なければ ``ValueError``
     - 近似 :math:`O(\log N)`
   * - ``pop(index=-1)``
     - 順位で削除して返す
     - 近似 :math:`O(\log N)`
   * - ``values[index]``
     - 順位アクセス。負のindex可
     - 近似 :math:`O(\log N)`
   * - ``value in values``
     - 存在判定
     - :math:`O(\log N)`
   * - ``bisect_left(value)``
     - ``value`` 未満の個数
     - 近似 :math:`O(\log N)`
   * - ``bisect_right(value)``
     - ``value`` 以下の個数
     - 近似 :math:`O(\log N)`
   * - ``count(value)``, ``index(value)``
     - 個数、最初の順位
     - 近似 :math:`O(\log N)`
   * - ``irange(minimum, maximum, inclusive=...)``
     - 値の範囲をiteratorで返す
     - 目安 :math:`O(\log N+K)`
   * - ``islice(left, right)``
     - 順位の半開区間をiteratorで返す
     - 目安 :math:`O(\log N+K)`
   * - iteration、``reversed(values)``
     - 全要素を順に列挙
     - :math:`O(N)`
   * - ``clear()``, ``copy()``
     - 全削除、shallow copy
     - :math:`O(N)`

sliceの返り値は通常のlistです。範囲が大きければ、要素数に比例する時間とメモリを
使います。列挙だけなら ``islice`` または ``irange`` のiteratorを使えます。

中央値と削除可能priority queue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

中央順位へ直接アクセスできるため、要素数が変わるmultisetの中央値を簡潔に扱えます。

.. testcode:: sorted-list-median

   from sortedcontainers import SortedList

   values = SortedList()
   for value in [8, 1, 5, 2, 9]:
       values.add(value)

   assert values[len(values) // 2] == 5
   values.remove(5)

   lower_median = values[(len(values) - 1) // 2]
   upper_median = values[len(values) // 2]
   assert (lower_median, upper_median) == (2, 8)

   minimum = values.pop(0)
   maximum = values.pop()
   print(minimum, maximum, list(values))

.. testoutput:: sorted-list-median

   1 9 [2, 8]

最小値の追加・取得だけなら ``heapq`` が軽量です。任意値削除、中央値、前後要素、順位が
必要なときに ``SortedList`` を選びます。

SortedKeyList
-------------

値そのものではなく ``key(value)`` の順で保持します。``SortedList(..., key=...)`` も
``SortedKeyList`` instanceを返します。``bisect_key_left`` などは値ではなく、抽出済み
のkeyを引数に取ります。

.. testcode:: sorted-key-list-complete

   from sortedcontainers import SortedKeyList

   tasks = SortedKeyList(
       [("write", 3), ("test", 1), ("review", 2)],
       key=lambda task: task[1],
   )

   assert list(tasks) == [
       ("test", 1),
       ("review", 2),
       ("write", 3),
   ]
   assert tasks.bisect_key_left(2) == 1
   assert tasks.bisect_key_right(2) == 2
   assert list(tasks.irange_key(1, 2)) == [
       ("test", 1),
       ("review", 2),
   ]

   tasks.add(("deploy", 0))
   print(list(tasks))

.. testoutput:: sorted-key-list-complete

   [('deploy', 0), ('test', 1), ('review', 2), ('write', 3)]

``add``、削除、順位アクセスなどは ``SortedList`` と同じで、近似
:math:`O(\log N)` です。追加APIは次の通りです。

.. list-table::
   :header-rows: 1
   :widths: 39 38 23

   * - API
     - 動作
     - 計算量
   * - ``bisect_key_left(key)``
     - 同じkeyの左端
     - 近似 :math:`O(\log N)`
   * - ``bisect_key_right(key)``
     - 同じkeyの右端
     - 近似 :math:`O(\log N)`
   * - ``irange_key(min_key, max_key, ...)``
     - key範囲をiteratorで返す
     - 目安 :math:`O(\log N+K)`
   * - ``key``
     - 構築時に指定した関数
     - 参照 :math:`O(1)`

格納中にobjectを変更して比較keyが変わると、内部のソート順が壊れます。変更する場合は
一度削除し、変更後に追加し直します。keyが同じ値同士の順序へ依存したい場合は、
``key=lambda item: (item.priority, item.id)`` のようにtie-breakもkeyへ含めます。

SortedSet
---------

組み込みsetの存在判定・集合演算と、ソート済みsequenceの順位アクセスを両立します。
同じ値を複数回追加しても1個だけ保持します。

.. testcode:: sorted-set-complete

   from sortedcontainers import SortedSet

   values = SortedSet([5, 1, 3, 3])
   assert list(values) == [1, 3, 5]
   assert 3 in values

   values.add(2)
   values.add(3)
   assert values[0] == 1
   assert values[-1] == 5
   assert values.bisect_left(3) == 2
   assert list(values.irange(2, 5, inclusive=(True, False))) == [2, 3]

   union = values | {4, 5, 6}
   intersection = values & {2, 3, 9}
   values.discard(99)

   assert list(union) == [1, 2, 3, 4, 5, 6]
   assert list(intersection) == [2, 3]
   print(list(values))

.. testoutput:: sorted-set-complete

   [1, 2, 3, 5]

主要APIと計算量
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 38 36 26

   * - API
     - 動作
     - 計算量
   * - ``SortedSet(iterable, key=None)``
     - 重複を除きkey順で構築
     - :math:`O(N\log N)`
   * - ``value in values``, ``len(values)``
     - 存在判定、要素数
     - :math:`O(1)`
   * - ``add``, ``discard``, ``remove``
     - 追加・削除
     - 近似 :math:`O(\log N)`
   * - ``values[index]``, ``pop(index)``
     - 順位参照・順位削除
     - 近似 :math:`O(\log N)`
   * - ``bisect_left/right``, ``index``
     - 順位・境界探索
     - 近似 :math:`O(\log N)`
   * - ``irange``, ``islice``
     - 値範囲・順位範囲の列挙
     - 目安 :math:`O(\log N+K)`
   * - iteration
     - ソート順に全列挙
     - :math:`O(N)`
   * - ``copy``, ``clear``
     - shallow copy・全削除
     - :math:`O(N)`
   * - ``union``, ``intersection``, ``difference`` など
     - 新しい ``SortedSet`` を返す集合演算
     - 入力・結果sizeに依存
   * - ``update``、各 ``*_update``
     - 自身を変更する集合演算
     - 入力・結果sizeに依存

``discard`` は値がなくても何もしませんが、``remove`` は ``KeyError`` を送出します。
集合演算の返り値は ``SortedSet`` です。hash可能かつ比較可能な値が必要で、格納中に
hash値や比較順を変えてはいけません。

SortedDict
----------

組み込みdictを値の保存に使い、keyを ``SortedList`` でソート順に管理するmappingです。
iteration、``keys``、``items``、``values`` はkey順です。``values`` が値そのものの順に
ソートされるわけではありません。

.. testcode:: sorted-dict-complete

   from sortedcontainers import SortedDict

   scores = SortedDict({5: "five", 1: "one", 3: "three"})
   scores[2] = "two"

   assert list(scores) == [1, 2, 3, 5]
   assert list(scores.items()) == [
       (1, "one"),
       (2, "two"),
       (3, "three"),
       (5, "five"),
   ]
   assert scores.peekitem(0) == (1, "one")
   assert scores.peekitem() == (5, "five")
   assert scores.keys()[2] == 3
   assert scores.items()[1] == (2, "two")

   assert scores.bisect_left(3) == 2
   assert list(scores.irange(2, 4)) == [2, 3]

   largest = scores.popitem()
   assert largest == (5, "five")
   print(list(scores.items()))

.. testoutput:: sorted-dict-complete

   [(1, 'one'), (2, 'two'), (3, 'three')]

主要APIと計算量
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 38 38 24

   * - API
     - 動作
     - 計算量
   * - ``len(mapping)``
     - key数
     - :math:`O(1)`
   * - ``mapping[key]``, ``get``, ``key in mapping``
     - keyによる参照・存在判定
     - 平均 :math:`O(1)`
   * - ``mapping[key] = value``
     - 追加または上書き
     - 近似 :math:`O(\log N)`
   * - ``del mapping[key]``, ``pop(key)``
     - keyによる削除
     - 近似 :math:`O(\log N)`
   * - ``setdefault(key, default)``
     - 参照し、なければ追加
     - 近似 :math:`O(\log N)`
   * - ``peekitem(index=-1)``
     - 順位のitemを変更せず返す
     - 近似 :math:`O(\log N)`
   * - ``popitem(index=-1)``
     - 順位のitemを削除して返す
     - :math:`O(\log N)`
   * - ``keys/items/values()[index]``
     - dynamic viewの順位アクセス
     - 近似 :math:`O(\log N)`
   * - ``bisect_left/right(key)``, ``index(key)``
     - keyの境界・順位
     - 近似 :math:`O(\log N)`
   * - ``irange``, ``islice``
     - key範囲・順位範囲の列挙
     - 目安 :math:`O(\log N+K)`
   * - iteration、``reversed(mapping)``
     - key順・逆key順に列挙
     - :math:`O(N)`
   * - ``copy``, ``clear``
     - shallow copy・全削除
     - :math:`O(N)`

``keys()``, ``items()``, ``values()`` はmappingの変更を反映するdynamic viewです。iteration
中に追加・削除すると ``RuntimeError`` になったり、全要素を列挙できなかったりする
可能性があります。変更対象を先に ``list(...)`` へ固定するか、別loopに分けます。

key関数による順序
^^^^^^^^^^^^^^^^^

``SortedDict`` のkey関数は最初の位置引数として渡します。keyword引数ではありません。

.. testcode:: sorted-dict-key-function

   from sortedcontainers import SortedDict

   descending = SortedDict(lambda key: -key)
   descending.update({1: "one", 3: "three", 2: "two"})

   assert list(descending) == [3, 2, 1]
   assert descending.peekitem(0) == (3, "three")
   assert descending.bisect_key_left(-2) == 1
   print(list(descending.items()))

.. testoutput:: sorted-dict-key-function

   [(3, 'three'), (2, 'two'), (1, 'one')]

keyはhash可能で、互いに比較可能でなければなりません。格納中にkeyのhash値や全順序が
変わるとdictとソート済みkey一覧の不変条件が壊れます。

典型的な使い分け
----------------

.. list-table::
   :header-rows: 1
   :widths: 42 29 29

   * - 必要な操作
     - 第一候補
     - 理由
   * - 追加せずbinary searchだけ
     - ``sorted`` + ``bisect``
     - 標準ライブラリだけで十分
   * - 追加しながら最小値だけ取得
     - ``heapq``
     - 小さく高速
   * - 任意値削除を伴うmultiset
     - ``SortedList``
     - 重複と値削除に対応
   * - 順位・中央値・前後要素
     - ``SortedList``
     - indexとbisectを併用可能
   * - 一意な値の順序集合
     - ``SortedSet``
     - membershipが :math:`O(1)`
   * - key順mapping
     - ``SortedDict``
     - dict参照と順序を両立
   * - 座標圧縮可能な個数・prefix sum
     - Fenwick Tree
     - 和を管理でき、外部依存なし
   * - 区間積・更新も必要
     - Segment Tree系
     - monoidやlazy更新を扱える

注意点
------

* judge環境に ``sortedcontainers`` がなければimportできません。提出先の利用可能library
  とversionを事前に確認します。
* 値・keyは全順序で比較可能でなければなりません。たとえばintとstrの混在は通常
  比較できません。
* 格納後に比較結果、key関数の結果、hash値が変わるmutable objectを直接変更しません。
* ``SortedList`` は重複を保持し、``SortedSet`` は除去します。
* ``remove`` の例外は ``SortedList`` では ``ValueError``、``SortedSet`` では
  ``KeyError`` です。存在しない値を無視するなら ``discard`` を使います。
* ``irange`` の既定は両端を含む値区間です。半開区間にするなら
  ``inclusive=(True, False)`` を指定します。``islice(left, right)`` は通常の
  0-indexed半開区間です。
* sliceや ``list(iterator)`` は結果全体を新しいlistへ格納します。
* iteration中にcontainerを変更しません。
* 内部属性や ``_reset``、``_check`` などunderscore付きAPIを競技コードから使いません。
* 公式の近似 :math:`O(\log N)` を、平衡木の厳密なworst-case保証とはみなしません。

参照した仕様
------------

このページはSorted Containers 2.4.0の公式 ``SortedList``、``SortedSet``、
``SortedDict`` API documentationおよびimplementation detailsに基づきます。offlineでの
利用時はこのページだけで主要操作を確認できます。

* `SortedList / SortedKeyList API
  <https://grantjenks.com/docs/sortedcontainers/sortedlist.html>`_
* `SortedSet API
  <https://grantjenks.com/docs/sortedcontainers/sortedset.html>`_
* `SortedDict API
  <https://grantjenks.com/docs/sortedcontainers/sorteddict.html>`_
* `Implementation Details
  <https://grantjenks.com/docs/sortedcontainers/implementation.html>`_
* `Performance at Scale
  <https://grantjenks.com/docs/sortedcontainers/performance-scale.html>`_
