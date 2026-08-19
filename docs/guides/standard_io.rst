標準入出力
==========

競技プログラミングで頻出する入力形式と出力方法をまとめます。通常は ``input``、
入力が多ければ ``sys.stdin.readline`` または ``sys.stdin.buffer`` を使います。

行単位で読む
------------

.. testcode:: standard-io-basic

   import io

   # 提出時: from sys import stdin; read_line = stdin.readline
   read_line = io.StringIO("5 3\n10 20 30 40 50\ncontest\n").readline

   n, query_count = map(int, read_line().split())
   values = list(map(int, read_line().split()))
   name = read_line().strip()

   assert n == len(values)
   assert query_count == 3
   assert values == [10, 20, 30, 40, 50]
   assert name == "contest"

``split()`` は連続する空白・tab・改行をまとめて区切ります。``split(" ")`` は半角
空白1文字だけを区切り、連続空白から空文字列を生成します。``map`` はiteratorなので、
後で再利用する列は ``list`` にします。

行列・文字grid
---------------

.. testcode:: standard-io-grid

   import io

   read_line = io.StringIO(
       "2 3\n1 2 3\n4 5 6\n.#.\n##.\n"
   ).readline
   height, width = map(int, read_line().split())
   matrix = [list(map(int, read_line().split())) for _ in range(height)]
   grid = [read_line().strip() for _ in range(height)]

   assert matrix[1][2] == 6
   assert grid[0][1] == "#"
   assert all(len(row) == width for row in matrix)
   assert all(len(row) == width for row in grid)

行頭・行末の空白自体がデータなら ``strip()`` は使いません。改行だけを除くなら
``rstrip("\r\n")`` を使います。

辺と1-indexed入力
------------------

.. testcode:: standard-io-edges

   import io

   read_line = io.StringIO(
       "4 3\n1 2 7\n2 4 5\n1 3 9\n"
   ).readline
   n, m = map(int, read_line().split())
   graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]
   edges = []
   for _ in range(m):
       from_vertex, to_vertex, weight = map(int, read_line().split())
       from_vertex -= 1
       to_vertex -= 1
       edges.append((from_vertex, to_vertex, weight))
       graph[from_vertex].append((to_vertex, weight))

   assert edges == [(0, 1, 7), (1, 3, 5), (0, 2, 9)]

問題文が1-indexedでも、読み取った直後に0-indexedへ変換すると後続処理での混在を
防げます。無向辺なら隣接リストへ逆向きも追加します。

複数テストケース
------------------

.. testcode:: standard-io-test-cases

   import io

   read_line = io.StringIO("3\n4\n1 2 3 4\n3\n5 5 5\n0\n\n").readline
   test_count = int(read_line())
   answers = []
   for _ in range(test_count):
       n = int(read_line())
       values = list(map(int, read_line().split()))
       assert len(values) == n
       answers.append(str(sum(values)))
   assert "\n".join(answers) == "10\n15\n0"

ケースごとに変わる配列やグラフはloop内で初期化します。空配列の入力行が存在するか
省略されるかは問題の入力仕様を確認してください。

bytesで読む
-----------

``sys.stdin.buffer.readline`` は ``bytes`` を返します。数値はdecodeせず ``int`` へ
渡せます。文字列として扱うtokenだけdecodeします。

.. testcode:: standard-io-bytes

   import io

   # 提出時: from sys import stdin; read_line = stdin.buffer.readline
   read_line = io.BytesIO(b"3\n10 20 30\nhello\n").readline
   n = int(read_line())
   values = list(map(int, read_line().split()))
   word = read_line().rstrip(b"\r\n").decode()
   assert n == len(values)
   assert word == "hello"

``row[index]`` は長さ1のbytesでなく整数を返します。非ASCII文字では1文字と1byteが
一致しないため、decodeして ``str`` として扱います。

入力全体をtoken化する
----------------------

.. testcode:: standard-io-all-tokens

   import io

   # 提出時: tokens = iter(sys.stdin.buffer.read().split())
   tokens = iter(io.BytesIO(b"4 10 20\n30 40\nword\n").read().split())
   n = int(next(tokens))
   values = [int(next(tokens)) for _ in range(n)]
   word = next(tokens).decode()
   assert values == [10, 20, 30, 40]
   assert word == "word"

入力全体と分割後の全tokenをメモリに保持します。行境界に意味がある入力、巨大入力、
対話型問題には使いません。

EOFまで読む
-----------

.. testcode:: standard-io-eof

   import io

   stream = io.BytesIO(b"1 2\n\n3 4\n5 6\n")
   pairs = []
   for line in stream:
       if not line.strip():
           continue
       pairs.append(tuple(map(int, line.split())))
   assert pairs == [(1, 2), (3, 4), (5, 6)]

``readline()`` のEOFはstr版が ``""``、bytes版が ``b""`` です。正当な空行は
``"\n"`` または ``b"\n"`` なので区別できます。

標準出力
--------

.. testcode:: standard-io-output

   import io

   output = io.StringIO()
   values = [3, 1, 4]
   print(*values, file=output)
   print(*values, sep=",", file=output)
   print(" ".join(map(str, values)), file=output)
   output.write("\n".join(["Yes", "No"]) + "\n")
   assert output.getvalue() == "3 1 4\n3,1,4\n3 1 4\nYes\nNo\n"

長い文字列へ ``+=`` を繰り返すのでなく、文字列listへ追加して最後に ``join`` します。
ただし非常に大きい出力は適度な単位で書き出します。

浮動小数
~~~~~~~~

.. testcode:: standard-io-float

   value = 1 / 3
   assert f"{value:.10f}" == "0.3333333333"
   assert f"{value:.15g}" == "0.333333333333333"

問題の許容誤差を確認し、固定小数点なら ``.10f``、有効数字なら ``.15g`` など十分な
桁数を出します。

対話型問題
----------

対話型問題ではjudgeへ送るたびにflushします。一括入力・出力の蓄積は使えません。

.. code-block:: python

   print("?", left, right, flush=True)
   response = int(input())
   print("!", answer, flush=True)

よくある間違い
--------------

* ``input`` を ``stdin.buffer.readline`` に変えるとstrからbytesになります。
* ``strip()`` は改行だけでなく両端の空白も除きます。
* ``map`` はlistではなく、一度しか走査できないiteratorです。
* 1-indexedと0-indexedを混在させないでください。
* 個数指定形式をEOFまで読む形式と取り違えないでください。
* listやsetをそのまま出力すると括弧やcommaも出ます。
* 通常問題で ``input("n = ")`` のようなpromptを出力してはいけません。

.. seealso::

   :doc:`data_io` — 入出力ガイドの目次へ戻る。
