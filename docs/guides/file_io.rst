ファイル入出力
==============

オンラインjudgeの通常問題は標準入出力を使います。手元で入力例を試すだけなら、
コードにfile名を埋め込まずshellのredirectを使う方法が簡単です。

.. code-block:: console

   python solution.py < input.txt
   python solution.py < input.txt > output.txt

相対pathはPythonファイルの場所ではなく、実行時のcurrent working directoryを基準に
解決されます。

Pathの構成要素を取得する
-------------------------

:class:`pathlib.Path` では文字列を手作業で ``split`` せず、propertyからfilename、
拡張子、親directoryなどを取得できます。これらのpropertyを見るだけでは、実際に
fileやdirectoryが存在する必要はありません。

.. list-table::
   :header-rows: 1
   :widths: 28 38 34

   * - property
     - 取得内容
     - 例
   * - ``path.name``
     - 最後の要素（filename）
     - ``report.csv``
   * - ``path.stem``
     - 最後の拡張子を除いたfilename
     - ``report``
   * - ``path.suffix``
     - 最後の拡張子
     - ``.csv``
   * - ``path.suffixes``
     - すべての拡張子のlist
     - ``[".tar", ".gz"]``
   * - ``path.parent``
     - 直接の親directory
     - ``data/archive``
   * - ``path.parents``
     - すべての親directory
     - ``parents[0]`` が直接の親
   * - ``path.parts``
     - pathを構成する各要素のtuple
     - ``("data", "archive", "report.csv")``
   * - ``path.anchor``
     - driveとrootを合わせた先頭部分
     - POSIX絶対pathなら ``/``

.. testcode:: file-io-path-parts

   from pathlib import Path

   path = Path("data") / "archive" / "report.csv"
   assert path.name == "report.csv"       # filename
   assert path.stem == "report"           # 拡張子なしfilename
   assert path.suffix == ".csv"            # 最後の拡張子
   assert path.suffixes == [".csv"]
   assert path.parent == Path("data/archive")
   assert path.parents[0] == Path("data/archive")
   assert path.parents[1] == Path("data")
   assert path.parts == ("data", "archive", "report.csv")
   assert path.anchor == ""                # 相対pathなのでanchorなし

複数拡張子と隠しfile
~~~~~~~~~~~~~~~~~~~~

``stem`` が除くのは最後の ``suffix`` だけです。すべての拡張子を確認する場合は
``suffixes`` を使います。

.. testcode:: file-io-path-suffixes

   from pathlib import Path

   archive = Path("backup.tar.gz")
   assert archive.name == "backup.tar.gz"
   assert archive.stem == "backup.tar"
   assert archive.suffix == ".gz"
   assert archive.suffixes == [".tar", ".gz"]

   hidden = Path(".gitignore")
   assert hidden.stem == ".gitignore"
   assert hidden.suffix == ""
   assert hidden.suffixes == []

名前や拡張子を変更したPathを作る
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

元の ``Path`` は変更されず、新しい ``Path`` が返ります。

.. testcode:: file-io-path-replace-name

   from pathlib import Path

   path = Path("data/report.csv")
   assert path.with_name("summary.json") == Path("data/summary.json")
   assert path.with_stem("summary") == Path("data/summary.csv")
   assert path.with_suffix(".json") == Path("data/report.json")
   assert path.with_suffix("") == Path("data/report")
   assert path == Path("data/report.csv")  # 元のPathは変わらない

``parent`` は文字列としてのpathを字句的に処理します。``..`` やsymlinkを解決した
絶対pathが必要なら ``resolve()`` を使います。存在確認は ``exists()``、種類の確認は
``is_file()`` / ``is_dir()`` です。

open mode早見表
---------------

.. list-table::
   :header-rows: 1
   :widths: 18 42 40

   * - mode
     - 動作
     - 注意
   * - ``"r"``
     - textを読む。既定値
     - なければ ``FileNotFoundError``
   * - ``"w"``
     - textを書き込む
     - 既存内容を消去、なければ作成
   * - ``"a"``
     - textを末尾へ追記
     - なければ作成
   * - ``"x"``
     - 新規text fileを作成
     - あれば ``FileExistsError``
   * - ``"rb"``, ``"wb"``
     - bytesを読み書き
     - ``encoding`` は指定しない
   * - ``"r+"``, ``"w+"``
     - 読み書き両方
     - cursor位置とflushに注意

テキスト全体を読む・書く
--------------------------

小さいfileなら :class:`pathlib.Path` が簡潔です。encodingを明示してlocale依存を
避けます。

.. testcode:: file-io-whole-text

   from pathlib import Path
   from tempfile import TemporaryDirectory

   with TemporaryDirectory() as temporary_directory:
       path = Path(temporary_directory) / "numbers.txt"
       path.write_text("3\n10 20 30\n", encoding="utf-8")
       lines = path.read_text(encoding="utf-8").splitlines()
       n = int(lines[0])
       values = list(map(int, lines[1].split()))
       assert n == len(values)
       assert sum(values) == 60

``read_text``、``read_bytes``、``read`` は全体をメモリに保持します。巨大なfileでは
行または固定sizeのblockに分けます。

行単位で読む
------------

``with`` blockを抜けると例外時もfileが閉じられます。

.. testcode:: file-io-lines

   from pathlib import Path
   from tempfile import TemporaryDirectory

   with TemporaryDirectory() as temporary_directory:
       path = Path(temporary_directory) / "edges.txt"
       path.write_text("4 3\n1 2 7\n2 4 5\n1 3 9\n", encoding="utf-8")

       with path.open("r", encoding="utf-8") as file:
           n, m = map(int, file.readline().split())
           edges = []
           for line in file:
               from_vertex, to_vertex, weight = map(int, line.split())
               edges.append((from_vertex - 1, to_vertex - 1, weight))

       assert n == 4
       assert len(edges) == m

テキストを書き込む
------------------

``write`` は改行を自動追加しません。``"w"`` は既存内容を消すため、追記は ``"a"``、
既存fileを保護する新規作成は ``"x"`` を使います。

.. testcode:: file-io-write

   from pathlib import Path
   from tempfile import TemporaryDirectory

   with TemporaryDirectory() as temporary_directory:
       path = Path(temporary_directory) / "answer.txt"
       with path.open("w", encoding="utf-8", newline="\n") as file:
           print(42, file=file)
           file.write("Yes\n")
       with path.open("a", encoding="utf-8", newline="\n") as file:
           file.write("No\n")
       assert path.read_text(encoding="utf-8") == "42\nYes\nNo\n"

読み込み時の既定 ``newline=None`` はCRLFなどを ``\n`` へ変換します。byte単位の
内容を保つ必要がある場合はbinary modeを使います。

.. seealso::

   :doc:`data_io` — 入出力ガイドの目次へ戻る。

   :doc:`csv_json` — CSV・JSONを扱う場合。

   :doc:`binary_io` — bytes、固定長record、binaryファイルを扱う場合。
