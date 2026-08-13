データ入出力ガイド
==================

競技プログラミングで頻出する標準入力の読み取り方と、標準出力の組み立て方を
入力形式別にまとめます。すべてPython標準ライブラリだけで動作します。

選び方
------

.. list-table:: 入力形式から選ぶ
   :header-rows: 1
   :widths: 35 39 26

   * - 入力形式
     - 基本形
     - 注意
   * - 1行に1個の整数
     - ``value = int(input())``
     - 改行は ``input`` が除く
   * - 1行に複数の整数
     - ``map(int, input().split())``
     - ``map`` はiterator
   * - 整数列
     - ``list(map(int, input().split()))``
     - 要素数を必要なら検証
   * - :math:`H\times W` の行列
     - ``[list(map(int, input().split())) for _ in range(h)]``
     - 外側が行、内側が列
   * - 空白なし文字グリッド
     - ``[input().strip() for _ in range(h)]``
     - 空白がデータなら ``strip`` 禁止
   * - 辺が :math:`M` 行
     - ``for _ in range(m): ...``
     - 1-indexedなら読取時に変換
   * - テストケースが :math:`T` 個
     - ``for case_index in range(t): ...``
     - ケースごとの初期化を忘れない
   * - 入力終了まで
     - ``for line in sys.stdin.buffer: ...``
     - 個数指定形式には使わない
   * - 非常に多い空白区切りtoken
     - ``sys.stdin.buffer.read().split()``
     - 入力全体をメモリに保持
   * - ローカルのテキストファイル
     - ``with open(path, encoding="utf-8") as file:``
     - 提出コードでは通常使わない
   * - CSV・JSONファイル
     - ``csv.reader``, ``json.load``
     - file形式を問題仕様と合わせる
   * - binaryファイル
     - ``open(path, "rb")``
     - bytes配置の仕様が必要
   * - 対話型問題
     - ``print(answer, flush=True)``
     - 一括読み込み不可

行単位で読む基本形
------------------

通常は ``input`` で十分です。入力が多い場合は、同じ使い方ができる
``sys.stdin.readline`` をローカル変数へ代入します。次の完全例は
``StringIO`` で標準入力相当のデータを再現しています。提出時はコメントで示した
1行に置き換えます。

.. testcode:: data-io-basic

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

   print(n, sum(values), name)

.. testoutput:: data-io-basic

   5 150 contest

``split()`` は連続する空白・tab・改行をまとめて区切ります。通常はこちらを使います。
``split(" ")`` は空白1文字だけを区切り、連続空白から空文字列を生成するため、多くの
入力では不向きです。``map`` は一度しか走査できないiteratorなので、後で再利用する
整数列は ``list`` にします。

行列・文字グリッド
------------------

行列は ``matrix[row][column]``、文字グリッドは ``grid[row][column]`` として持つのが
基本です。どちらも0-indexedです。

.. testcode:: data-io-grid

   import io

   read_line = io.StringIO(
       "2 3\n"
       "1 2 3\n"
       "4 5 6\n"
       ".#.\n"
       "##.\n"
   ).readline

   height, width = map(int, read_line().split())
   matrix = [
       list(map(int, read_line().split()))
       for _ in range(height)
   ]
   grid = [read_line().strip() for _ in range(height)]

   assert all(len(row) == width for row in matrix)
   assert all(len(row) == width for row in grid)
   assert matrix[1][2] == 6
   assert grid[0][1] == "#"

   print([sum(row) for row in matrix])
   print(sum(cell == "#" for row in grid for cell in row))

.. testoutput:: data-io-grid

   [6, 15]
   3

行頭・行末の空白自体がデータなら ``strip()`` を使ってはいけません。改行だけを除く
場合は ``rstrip("\n")``、CRLFも考慮するなら ``rstrip("\r\n")`` を使います。
ただし ``rstrip("\r\n")`` は末尾にあるCRまたはLFをすべて除く操作であり、任意の
1改行だけを除く専用操作ではありません。

グラフの辺と1-indexed入力
--------------------------

問題文の頂点が1始まりでも、ライブラリ内では0-indexedへ変換します。変換は辺を
読み取った直後に1回だけ行うと、後続処理での混在を防げます。

.. testcode:: data-io-edges

   import io

   read_line = io.StringIO(
       "4 3\n"
       "1 2 7\n"
       "2 4 5\n"
       "1 3 9\n"
   ).readline

   n, m = map(int, read_line().split())
   graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]
   edges: list[tuple[int, int, int]] = []

   for _ in range(m):
       from_vertex, to_vertex, weight = map(int, read_line().split())
       from_vertex -= 1
       to_vertex -= 1
       edges.append((from_vertex, to_vertex, weight))
       graph[from_vertex].append((to_vertex, weight))

   assert edges == [(0, 1, 7), (1, 3, 5), (0, 2, 9)]
   assert graph[0] == [(1, 7), (2, 9)]
   print(edges)

.. testoutput:: data-io-edges

   [(0, 1, 7), (1, 3, 5), (0, 2, 9)]

無向辺では逆向きも隣接リストへ追加しますが、辺一覧には入力1行につき1要素だけを
保存する方が自然な場合があります。自己ループ・多重辺を問題が許すかも確認します。

複数テストケース
----------------

ケースごとに変わる配列やグラフはループ内で初期化します。出力をlistに蓄え、最後に
まとめて出すと簡潔です。

.. testcode:: data-io-test-cases

   import io

   read_line = io.StringIO(
       "3\n"
       "4\n1 2 3 4\n"
       "3\n5 5 5\n"
       "0\n\n"
   ).readline

   test_count = int(read_line())
   answers: list[str] = []

   for _ in range(test_count):
       n = int(read_line())
       values = list(map(int, read_line().split()))
       assert len(values) == n
       answers.append(str(sum(values)))

   print("\n".join(answers))

.. testoutput:: data-io-test-cases

   10
   15
   0

空配列の入力行が空行になる形式では、``split()`` の結果は空listです。一方、多くの
問題は :math:`N=0` のとき、その配列の入力行自体を省略します。どちらなのかを入力
仕様で確認してください。

bytesによる高速な行入力
-----------------------

``sys.stdin.buffer.readline`` は ``bytes`` を返します。``int`` はbytesを直接変換でき、
``split`` も利用できるため、数値だけならdecodeは不要です。文字列として扱うtokenだけ
``decode()`` します。

.. testcode:: data-io-bytes

   import io

   # 提出時: from sys import stdin; read_line = stdin.buffer.readline
   read_line = io.BytesIO(b"3\n10 20 30\nhello\n").readline

   n = int(read_line())
   values = list(map(int, read_line().split()))
   word = read_line().rstrip(b"\r\n").decode()

   assert n == len(values)
   assert word == "hello"
   print(sum(values), word)

.. testoutput:: data-io-bytes

   60 hello

文字を1byteずつ扱うだけならdecodeせず、ASCIIコードとして利用する方法もあります。
ただし ``row[index]`` は長さ1のbytesでなく ``int`` を返します。日本語などの
非ASCII文字では1文字と1byteが一致しないため、decodeして ``str`` として扱います。

入力全体をtoken化する
----------------------

大量の空白区切り整数では、入力全体を一度だけ読み込む方法が簡潔です。入力サイズ分の
bytesと、分割した各tokenを保持するため、メモリ制限に余裕がある場合だけ使います。
行の境界が意味を持つ入力や対話型問題には使えません。

.. testcode:: data-io-all-tokens

   import io

   # 提出時:
   # from sys import stdin
   # tokens = iter(stdin.buffer.read().split())
   tokens = iter(io.BytesIO(b"4 10 20\n30 40\nword\n").read().split())

   n = int(next(tokens))
   values = [int(next(tokens)) for _ in range(n)]
   word = next(tokens).decode()

   assert values == [10, 20, 30, 40]
   assert word == "word"
   print(n, sum(values), word)

.. testoutput:: data-io-all-tokens

   4 100 word

入力終了まで読む
----------------

行数が指定されず、EOFまで同じ形式が続く場合は標準入力をそのまま反復します。
空行を無視してよいかは問題仕様によります。

.. testcode:: data-io-eof

   import io

   stream = io.BytesIO(b"1 2\n\n3 4\n5 6\n")
   pairs: list[tuple[int, int]] = []
   for line in stream:
       if not line.strip():
           continue
       left, right = map(int, line.split())
       pairs.append((left, right))

   assert pairs == [(1, 2), (3, 4), (5, 6)]
   print(sum(left + right for left, right in pairs))

.. testoutput:: data-io-eof

   21

``readline()`` を使う場合、EOFではstr版が ``""``、bytes版が ``b""`` を返します。
正当な空行も改行文字を含む ``"\n"`` または ``b"\n"`` なので区別できます。

ファイル入出力
--------------

オンラインjudgeの通常問題は標準入力・標準出力を使うため、提出コードにローカルの
file名を埋め込みません。手元で入力例を試すだけなら、コードを変更せずshellの
redirectを使う方法が簡単です。

.. code-block:: console

   python solution.py < input.txt
   python solution.py < input.txt > output.txt

問題自体がfileの読み書きを要求する場合や、ローカルのテストデータを処理する場合は
``open`` または :class:`pathlib.Path` を使います。相対pathはPythonファイルの場所
ではなく、実行時のcurrent working directoryを基準に解決されます。

open mode早見表
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 18 42 40

   * - mode
     - 動作
     - fileが存在するとき・しないとき
   * - ``"r"``
     - textを読み込む。既定値
     - 存在しなければ ``FileNotFoundError``
   * - ``"w"``
     - textを書き込む
     - 存在すれば内容を消去、なければ作成
   * - ``"a"``
     - textを末尾へ追記する
     - 存在しなければ作成
   * - ``"x"``
     - 新しいtext fileを作成する
     - 存在すれば ``FileExistsError``
   * - ``"rb"``, ``"wb"``
     - binaryをbytesとして読み書きする
     - ``encoding`` は指定しない
   * - ``"r+"``, ``"w+"``
     - 読み書きの両方を許す
     - cursor位置の管理が必要

``+`` modeは同じfile objectで読み書きできますが、cursor位置とflushを意識する必要が
あるため、単純な競技用処理では読み込みと書き込みを分ける方が安全です。

テキスト全体を読む
^^^^^^^^^^^^^^^^^^

小さなfileなら ``Path.read_text`` と ``write_text`` が簡潔です。``encoding`` を明示し、
処理系のlocaleに依存しないようにします。次の例は一時directory内だけで動作し、終了時
にfileを削除します。

.. testcode:: data-io-file-whole-text

   from pathlib import Path
   from tempfile import TemporaryDirectory

   with TemporaryDirectory() as temporary_directory:
       path = Path(temporary_directory) / "numbers.txt"
       written = path.write_text(
           "3\n10 20 30\n",
           encoding="utf-8",
       )
       assert written == len("3\n10 20 30\n")

       text = path.read_text(encoding="utf-8")
       lines = text.splitlines()
       n = int(lines[0])
       values = list(map(int, lines[1].split()))

       assert n == len(values)
       print(path.name, sum(values))

.. testoutput:: data-io-file-whole-text

   numbers.txt 60

``read_text`` と ``read`` はfile全体をメモリに保持します。巨大なfileでは次のように
line iteratorを使います。

行単位・token単位で読む
^^^^^^^^^^^^^^^^^^^^^^^^

``with`` blockを抜けると、例外が発生した場合もfileが閉じられます。行単位の反復は
改行を含むstrを順に返すため、入力全体を保持しません。

.. testcode:: data-io-file-lines

   from pathlib import Path
   from tempfile import TemporaryDirectory

   with TemporaryDirectory() as temporary_directory:
       path = Path(temporary_directory) / "edges.txt"
       path.write_text(
           "4 3\n1 2 7\n2 4 5\n1 3 9\n",
           encoding="utf-8",
       )

       with path.open("r", encoding="utf-8") as file:
           n, m = map(int, file.readline().split())
           edges = []
           for line in file:
               if not line.strip():
                   continue
               from_vertex, to_vertex, weight = map(int, line.split())
               edges.append(
                   (from_vertex - 1, to_vertex - 1, weight)
               )

       assert n == 4
       assert len(edges) == m
       print(edges)

.. testoutput:: data-io-file-lines

   [(0, 1, 7), (1, 3, 5), (0, 2, 9)]

空白区切りtokenだけが必要で、file sizeに余裕があるなら
``path.read_bytes().split()`` も使えます。これは ``sys.stdin.buffer.read().split()``
と同様にfile全体と全tokenをメモリへ保持します。

テキストを書き込む
^^^^^^^^^^^^^^^^^^

``"w"`` は既存内容を消してから書き、``"a"`` は末尾へ追記します。意図しない消去を
避けたい新規fileには ``"x"`` を使います。``write`` は改行を自動追加しません。

.. testcode:: data-io-file-write

   from pathlib import Path
   from tempfile import TemporaryDirectory

   with TemporaryDirectory() as temporary_directory:
       path = Path(temporary_directory) / "answer.txt"

       with path.open(
           "w",
           encoding="utf-8",
           newline="\n",
       ) as file:
           print(42, file=file)
           file.write("Yes\n")

       with path.open(
           "a",
           encoding="utf-8",
           newline="\n",
       ) as file:
           file.write("No\n")

       assert path.read_text(encoding="utf-8") == "42\nYes\nNo\n"
       print(path.read_text(encoding="utf-8"), end="")

.. testoutput:: data-io-file-write

   42
   Yes
   No

``newline="\n"`` は書き込み時の改行をLFへ揃える指定です。読み込み時の既定
``newline=None`` は ``\n``、``\r\n``、``\r`` を認識し、返す改行を ``\n`` へ
変換します。byte単位の内容を保つ必要がある場合はbinary modeを使います。

CSV
^^^

comma区切りに引用符、commaを含むfield、改行を含むfieldがあり得るなら、手作業の
``split(",")`` ではなく標準ライブラリの :mod:`csv` を使います。fileを開くときは
``newline=""`` を指定し、改行処理をcsv moduleへ任せます。

.. testcode:: data-io-file-csv

   import csv
   from pathlib import Path
   from tempfile import TemporaryDirectory

   with TemporaryDirectory() as temporary_directory:
       path = Path(temporary_directory) / "scores.csv"

       with path.open(
           "w",
           encoding="utf-8",
           newline="",
       ) as file:
           writer = csv.writer(file, lineterminator="\n")
           writer.writerow(["name", "score"])
           writer.writerow(["Alice", 90])
           writer.writerow(["Smith, Bob", 85])

       with path.open(
           "r",
           encoding="utf-8",
           newline="",
       ) as file:
           rows = list(csv.DictReader(file))

       assert rows == [
           {"name": "Alice", "score": "90"},
           {"name": "Smith, Bob", "score": "85"},
       ]
       print([(row["name"], int(row["score"])) for row in rows])

.. testoutput:: data-io-file-csv

   [('Alice', 90), ('Smith, Bob', 85)]

CSVには型情報がないため、readerが返すfieldはstrです。delimiter、quote、headerの有無
などのdialectは入力仕様に合わせます。

JSON
^^^^

JSONのobject、array、number、string、boolean、nullは、それぞれ主にPythonのdict、
list、int/float、str、bool、``None`` へ変換されます。JSONはtupleやset、任意精度の
decimalなどをそのまま保存する形式ではありません。

.. testcode:: data-io-file-json

   import json
   from pathlib import Path
   from tempfile import TemporaryDirectory

   data = {
       "name": "東京",
       "values": [10, 20, 30],
       "enabled": True,
   }

   with TemporaryDirectory() as temporary_directory:
       path = Path(temporary_directory) / "data.json"

       with path.open("w", encoding="utf-8") as file:
           json.dump(
               data,
               file,
               ensure_ascii=False,
               indent=2,
           )

       with path.open("r", encoding="utf-8") as file:
           loaded = json.load(file)

       assert loaded == data
       print(loaded["name"], sum(loaded["values"]))

.. testoutput:: data-io-file-json

   東京 60

``json.load(file)`` はfileから読み、``json.loads(text)`` は既にあるstrから読みます。
書き込み側は ``dump`` と ``dumps`` です。信頼できないJSONを読んでも任意コードは
実行されませんが、極端に深い・大きいデータによる資源消費には注意します。

binary file
^^^^^^^^^^^

binary modeはbytesをそのまま読み書きします。整数などの配置が決まっている形式には
:mod:`struct` を使えますが、byte order、符号、幅、要素数をfile仕様と完全に合わせる
必要があります。次の ``<Ih`` はlittle endianのunsigned 32-bit整数とsigned 16-bit
整数を表します。

.. testcode:: data-io-file-binary

   from pathlib import Path
   import struct
   from tempfile import TemporaryDirectory

   record_format = struct.Struct("<Ih")

   with TemporaryDirectory() as temporary_directory:
       path = Path(temporary_directory) / "record.bin"
       with path.open("wb") as file:
           file.write(record_format.pack(100_000, -123))

       with path.open("rb") as file:
           raw = file.read(record_format.size)
           if len(raw) != record_format.size:
               raise EOFError("incomplete record")
           identifier, delta = record_format.unpack(raw)

       assert path.read_bytes() == b"\xa0\x86\x01\x00\x85\xff"
       print(identifier, delta, record_format.size)

.. testoutput:: data-io-file-binary

   100000 -123 6

画像、圧縮file、独自binary formatには、それぞれの仕様や対応moduleが必要です。
textとして無理にdecodeせず、必要なformatだけを明示的に扱います。

標準出力
--------

少量なら ``print``、多数の行なら文字列をlistに集めて ``"\n".join`` で出力します。
``join`` の要素はstrでなければならないため、整数には ``map(str, values)`` を使います。

.. testcode:: data-io-output

   import io

   output = io.StringIO()
   values = [3, 1, 4]

   print(*values, file=output)
   print(*values, sep=",", file=output)
   print(" ".join(map(str, values)), file=output)

   answers = ["Yes", "No", "Yes"]
   output.write("\n".join(answers) + "\n")

   result = output.getvalue()
   assert result == "3 1 4\n3,1,4\n3 1 4\nYes\nNo\nYes\n"
   print(result, end="")

.. testoutput:: data-io-output

   3 1 4
   3,1,4
   3 1 4
   Yes
   No
   Yes

長い文字列を ``answer += piece`` で繰り返し連結すると二次時間になる場合があります。
要素をlistへ追加して最後に ``join`` します。ただし、全出力を保持するとメモリを使う
ため、非常に大きい場合は適度な単位で出力します。

浮動小数の出力
--------------

問題の許容誤差を確認し、十分な桁数を出します。固定小数点ならf-stringの
``.10f``、有効数字なら ``.15g`` などを使います。浮動小数を厳密な等号判定へ
使わない点にも注意してください。

.. testcode:: data-io-float-output

   value = 1 / 3
   print(f"{value:.10f}")
   print(f"{value:.15g}")

.. testoutput:: data-io-float-output

   0.3333333333
   0.333333333333333

対話型問題
----------

対話型問題では、出力をjudgeへ送るたびにflushします。入力全体をEOFまで読む方法や、
回答を最後まで蓄える方法は使えません。通常問題で毎回flushすると遅くなるため、
必要な場合だけ指定します。

.. code-block:: python

   # 問題固有のprotocolに従う例。これは通常のdoctestでは実行しない。
   print("?", left, right, flush=True)
   response = int(input())

   print("!", answer, flush=True)

judgeから ``-1`` などの異常終了値が定義されている場合は、直ちにプログラムを終了
します。質問回数の上限、出力書式、flushのタイミングは問題文を優先してください。

よくある間違い
--------------

* ``input`` を ``sys.stdin.buffer.readline`` に置き換えると返り値がstrからbytesへ
  変わります。文字列操作を混在させないでください。
* ``strip()`` は改行だけでなく両端の空白も消します。空白自体がデータなら使いません。
* ``map`` はlistではなく、一度しか走査できないiteratorです。
* 問題文の1-indexedと実装の0-indexedを混在させないでください。
* 行数・要素数が指定されているなら、EOFまで読むのでなく指定個数だけ読みます。
* 出力するlistやsetを誤ってそのまま ``print`` すると、括弧やcommaも出力されます。
* setやdict由来の順序を期待せず、必要なら明示的に ``sorted`` します。
* 通常問題でprompt文字列を ``input("n = ")`` のように出力してはいけません。
* 対話型問題以外では、入力不足を無限loopで待つようなscannerを作らないでください。
* ``"w"`` は既存fileを確認なしで空にします。追記なら ``"a"``、新規作成限定なら
  ``"x"`` を選びます。
* ``open`` したfileは ``with`` で管理し、正常終了時だけでなく例外時にも閉じます。
* text fileでは ``encoding`` を明示し、binary fileでは指定しません。
* file sizeが大きい場合は ``read``、``read_text``、``read_bytes`` で一括読込せず、
  行や固定sizeのblockに分けます。
