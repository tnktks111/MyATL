NumPy行列演算ガイド
===================

NumPyを利用できる環境で、密なベクトル・行列を短く記述するための早見表です。
MyATL本体の実装は標準ライブラリだけで動作しますが、このページの例には ``numpy``
が必要です。

使いどころ
----------

密行列の積、線形漸化式、浮動小数の連立一次方程式、配列全体への同じ演算などに
向きます。疎なグラフは隣接リスト、法付き行列累乗でオーバーフローを避けつつ速度も
必要な場合は通常のPythonによる専用実装を選ぶ方が安全です。

基本操作の完全例
----------------

``shape`` は各軸の長さ、``dtype`` は要素型です。``axis=0`` は行を畳んで列ごと、
``axis=1`` は列を畳んで行ごとに集約します。

.. testcode:: numpy-matrix-basics

   import numpy as np

   matrix = np.array(
       [
           [1, 2, 3],
           [4, 5, 6],
       ],
       dtype=np.int64,
   )

   assert matrix.shape == (2, 3)
   assert matrix[1, 2] == 6
   assert matrix[0].tolist() == [1, 2, 3]
   assert matrix[:, 1].tolist() == [2, 5]
   assert matrix[:, 1:3].tolist() == [[2, 3], [5, 6]]

   row_sums = matrix.sum(axis=1)
   column_maximums = matrix.max(axis=0)
   maximum_positions = matrix.argmax(axis=1)

   zeros = np.zeros((2, 3), dtype=np.int64)
   ones = np.ones((2, 3), dtype=np.int64)
   identity = np.eye(3, dtype=np.int64)
   assert zeros.sum() == 0
   assert ones.sum() == 6
   assert identity.tolist() == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

   print(row_sums.tolist())
   print(column_maximums.tolist())
   print(maximum_positions.tolist())

.. testoutput:: numpy-matrix-basics

   [6, 15]
   [4, 5, 6]
   [2, 2]

要素積・行列積・転置
--------------------

``*`` は同じ位置の要素同士を掛け、``@`` は行列積を計算します。数学上の行列積には
必ず ``@`` を使います。行列積 :math:`A_{m\times k}B_{k\times n}` の計算量は
通常 :math:`O(mkn)` ですが、NumPy内部の実装により定数倍が小さくなる場合があります。

.. testcode:: numpy-matrix-products

   import numpy as np

   left = np.array([[1, 2], [3, 4]], dtype=np.int64)
   right = np.array([[5, 6], [7, 8]], dtype=np.int64)

   elementwise = left * right
   product = left @ right
   transpose = left.T

   assert elementwise.tolist() == [[5, 12], [21, 32]]
   assert product.tolist() == [[19, 22], [43, 50]]
   assert transpose.tolist() == [[1, 3], [2, 4]]

   vector = np.array([10, 20], dtype=np.int64)
   assert (left @ vector).tolist() == [50, 110]

   print(product.tolist())

.. testoutput:: numpy-matrix-products

   [[19, 22], [43, 50]]

形状変更・連結・ブロードキャスト
--------------------------------

``reshape`` は要素数を保って形状を変更します。``concatenate`` は既存の軸に沿って
連結し、``stack`` は新しい軸を作ります。形状の異なる配列を演算するときは、末尾の
軸から長さが等しいか、どちらかが1でなければなりません。

.. testcode:: numpy-matrix-shape

   import numpy as np

   values = np.arange(6, dtype=np.int64)
   matrix = values.reshape(2, 3)
   row_offset = np.array([10, 20, 30], dtype=np.int64)

   # (2, 3) と (3,) のブロードキャスト。
   shifted = matrix + row_offset
   assert shifted.tolist() == [[10, 21, 32], [13, 24, 35]]

   top_and_bottom = np.concatenate([matrix, matrix], axis=0)
   new_axis = np.stack([matrix, matrix], axis=0)
   assert top_and_bottom.shape == (4, 3)
   assert new_axis.shape == (2, 2, 3)

   # 条件を満たす要素だけを選ぶ。
   assert matrix[matrix % 2 == 0].tolist() == [0, 2, 4]

   print(shifted.tolist())

.. testoutput:: numpy-matrix-shape

   [[10, 21, 32], [13, 24, 35]]

行列累乗による線形漸化式
--------------------------

``np.linalg.matrix_power(matrix, exponent)`` は正方行列を繰り返し二乗法で累乗します。
:math:`N\times N` 行列なら計算量の目安は :math:`O(N^3\log K)` です。次の例では
Fibonacci数を求めます。

.. testcode:: numpy-matrix-power

   import numpy as np

   transition = np.array([[1, 1], [1, 0]], dtype=np.int64)
   powered = np.linalg.matrix_power(transition, 10)

   # powered[0, 1] は F_10。
   assert powered.tolist() == [[89, 55], [55, 34]]
   print(int(powered[0, 1]))

.. testoutput:: numpy-matrix-power

   55

法付き行列累乗
--------------

``np.linalg.matrix_power(matrix, exponent) % modulus`` は、剰余を取る前の途中計算で
固定幅整数がオーバーフローするため一般には安全ではありません。以下は
``dtype=object`` によりPythonの多倍長整数を使い、各行列積の直後に剰余を取る完全例
です。正確ですが、NumPyの高速な固定幅整数演算は利用できません。

.. testcode:: numpy-matrix-power-mod

   import numpy as np


   def matrix_power_mod(
       matrix: np.ndarray,
       exponent: int,
       modulus: int,
   ) -> np.ndarray:
       """正方行列を法 ``modulus`` で ``exponent`` 乗する。"""
       if exponent < 0:
           raise ValueError("exponent must be non-negative")
       if modulus <= 0:
           raise ValueError("modulus must be positive")

       # 呼び出し元の配列を変更しないよう、必ずコピーする。
       base = np.array(matrix, dtype=object, copy=True)
       if base.ndim != 2 or base.shape[0] != base.shape[1]:
           raise ValueError("matrix must be square")

       result = np.eye(base.shape[0], dtype=object)
       base %= modulus
       while exponent:
           if exponent & 1:
               result = (result @ base) % modulus
           base = (base @ base) % modulus
           exponent >>= 1
       return result


   transition = np.array([[1, 1], [1, 0]], dtype=object)
   powered = matrix_power_mod(transition, 100, 1_000_000_007)

   assert powered[0, 1] == 687_995_182
   print(powered.tolist())

.. testoutput:: numpy-matrix-power-mod

   [[782204094, 687995182], [687995182, 94208912]]

``int64`` のまま法付き積をしてよいのは、内積の途中値まで含めて
:math:`2^{63}-1` 以下だと証明できる場合だけです。行列サイズを :math:`N`、各要素を
``[0, modulus)`` に正規化済みとすると、十分条件の一つは
``N * (modulus - 1) ** 2 <= np.iinfo(np.int64).max`` です。

連立一次方程式
--------------

浮動小数の連立一次方程式 :math:`Ax=b` には ``np.linalg.solve`` を使います。
``inv(A) @ b`` と逆行列を明示的に作る必要はありません。結果は丸め誤差を含むため、
``==`` ではなく ``np.allclose`` で検証します。

.. testcode:: numpy-matrix-solve

   import numpy as np

   coefficients = np.array([[2.0, 1.0], [1.0, -1.0]])
   constants = np.array([5.0, 1.0])

   solution = np.linalg.solve(coefficients, constants)
   assert np.allclose(solution, np.array([2.0, 1.0]))
   assert np.allclose(coefficients @ solution, constants)

   print(solution.tolist())

.. testoutput:: numpy-matrix-solve

   [2.0, 1.0]

到達可能性をブロードキャストで更新する例
------------------------------------------

小さな密グラフなら、Warshall法の1段をboolean配列のブロードキャストで記述できます。
計算量は :math:`O(N^3)`、空間は :math:`O(N^2)` です。大きな疎グラフではDFS・BFSや
SCCを使用してください。

.. testcode:: numpy-warshall

   import numpy as np

   n = 4
   reachable = np.eye(n, dtype=bool)
   for from_vertex, to_vertex in [(0, 1), (1, 2), (2, 1), (2, 3)]:
       reachable[from_vertex, to_vertex] = True

   for middle in range(n):
       reachable |= (
           reachable[:, middle, None]
           & reachable[None, middle, :]
       )

   assert reachable[0].tolist() == [True, True, True, True]
   assert reachable[3].tolist() == [False, False, False, True]
   print(reachable.astype(np.int8).tolist())

.. testoutput:: numpy-warshall

   [[1, 1, 1, 1], [0, 1, 1, 1], [0, 1, 1, 1], [0, 0, 0, 1]]

よく使う操作
------------

.. list-table::
   :header-rows: 1
   :widths: 34 34 32

   * - 目的
     - 操作
     - 注意
   * - 最小値・最大値と位置
     - ``min``, ``max``, ``argmin``, ``argmax``
     - 必要なら ``axis`` を指定
   * - 条件を満たす位置
     - ``np.where(condition)``
     - 戻り値は軸ごとの配列のtuple
   * - 条件付きの値
     - ``np.where(condition, x, y)``
     - ``x`` と ``y`` はbroadcastされる
   * - 並べ替え
     - ``np.sort``, ``np.argsort``
     - 既定では最後の軸
   * - 一意化
     - ``np.unique``
     - 既定ではソート済み結果
   * - 内積・外積
     - ``np.dot``, ``np.outer``
     - 2次元行列積には ``@`` が明瞭
   * - 行列式・階数
     - ``np.linalg.det``, ``matrix_rank``
     - 浮動小数誤差を含む
   * - 固有値
     - ``np.linalg.eig``, ``eigvalsh``
     - 対称行列には ``eigvalsh``

基数変換
--------

``np.base_repr(number, base)`` は整数を2〜36進数の文字列へ変換します。標準の
``format`` が直接扱わない3進数などにも使えます。

.. testcode:: numpy-base-repr

   import numpy as np

   assert np.base_repr(10, 2) == "1010"
   assert np.base_repr(10, 3) == "101"
   assert np.base_repr(255, 16) == "FF"
   assert np.base_repr(-10, 3) == "-101"
   assert int(np.base_repr(100, 7), 7) == 100

逆変換にはPython標準の ``int(text, base)`` を使います。詳細、自前実装、2の補数は
:doc:`number_bases` を参照してください。``padding`` は全体幅でなく、追加するゼロの
個数です。

よくある間違い
--------------

* ``np.matrix`` は使わず、常に ``np.ndarray`` を使います。
* ``*`` は行列積ではありません。行列積には ``@`` を使います。
* ``(n,)`` の一次元配列と ``(n, 1)`` の列ベクトルは別の形状です。
* 基本スライスは元配列とメモリを共有するviewになり得ます。独立させるなら
  ``matrix[:, :2].copy()`` とします。
* ``int64`` は約 :math:`9.22\times10^{18}` を超えると例外なしで桁あふれする場合が
  あります。剰余を最後に取るだけでは防げません。
* ``dtype=object`` はPython整数を保持できますが、多くの場合NumPyによる高速化を
  失います。
* ``np.linalg`` の結果は原則として浮動小数です。整数・有理数・法上での厳密解法を
  必要とする問題には、その代数系に対応した実装を使います。
* 配列の生成・型変換・連結は新しい配列を確保することがあります。短い処理では
  通常のPythonリストの方が速い場合もあります。
