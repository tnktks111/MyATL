データ入出力ガイド
==================

標準入力、ローカルファイル、CSV・JSONの詳細を用途別ページへ分けています。
まず処理するデータの形式から選んでください。すべてPython標準ライブラリだけで
動作します。

用途から選ぶ
------------

.. list-table::
   :header-rows: 1
   :widths: 25 42 33

   * - ページ
     - 対象
     - 主な内容
   * - :doc:`standard_io`
     - 競技プログラミングの標準入力・標準出力
     - ``input``、行列、辺、EOF、bytes、出力
   * - :doc:`file_io`
     - Pathと通常のテキストファイル
     - ``open``、mode、``Path``
   * - :doc:`binary_io`
     - binaryファイル・固定長record
     - ``bytes``、``struct``、``seek``
   * - :doc:`csv_json`
     - CSV・JSONファイル
     - ``csv.reader``、``DictReader``、``json.load``

入力形式早見表
--------------

.. list-table::
   :header-rows: 1
   :widths: 35 39 26

   * - 入力形式
     - 基本形
     - 詳細
   * - 1行に1個の整数
     - ``value = int(input())``
     - :doc:`standard_io`
   * - 1行に複数の整数・整数列
     - ``list(map(int, input().split()))``
     - :doc:`standard_io`
   * - :math:`H\times W` の行列・grid
     - list comprehension
     - :doc:`standard_io`
   * - 辺が :math:`M` 行
     - ``for _ in range(m): ...``
     - :doc:`standard_io`
   * - 入力終了まで
     - ``for line in sys.stdin.buffer: ...``
     - :doc:`standard_io`
   * - 非常に多い空白区切りtoken
     - ``sys.stdin.buffer.read().split()``
     - :doc:`standard_io`
   * - テキストファイル
     - ``with open(...) as file:``
     - :doc:`file_io`
   * - binaryファイル
     - ``open(path, "rb")`` / ``struct``
     - :doc:`binary_io`
   * - CSV
     - ``csv.reader`` / ``csv.DictReader``
     - :doc:`csv_json`
   * - JSON
     - ``json.load``
     - :doc:`csv_json`

最小例
------

.. testcode:: data-io-hub-basic

   import io

   # 提出時: from sys import stdin; read_line = stdin.readline
   read_line = io.StringIO("3\n10 20 30\n").readline
   n = int(read_line())
   values = list(map(int, read_line().split()))
   assert len(values) == n
   assert sum(values) == 60

.. toctree::
   :maxdepth: 1
   :hidden:

   standard_io
   file_io
   binary_io
   csv_json
