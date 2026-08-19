CSV・JSON
=========

CSVの引用符・delimiter・headerは :mod:`csv` に任せ、JSONは :mod:`json` でPythonの
dict/listなどと相互変換します。

CSVを読む
---------

基本
~~~~

``csv.reader`` は各行を文字列listとして返します。

.. testcode:: csv-reader-basic

   import csv
   import io

   file = io.StringIO("name,score\nAlice,90\nBob,85\n")
   reader = csv.reader(file)
   rows = []
   for row in reader:
       rows.append(row)

   assert rows == [
       ["name", "score"],
       ["Alice", "90"],
       ["Bob", "85"],
   ]

fileから読む場合は、CSV module自身に改行を処理させるため ``newline=""`` を指定
します。

.. code-block:: python

   with open("data.csv", "r", encoding="utf-8", newline="") as file:
       reader = csv.reader(file)
       for row in reader:
           ...

delimiterを指定する
~~~~~~~~~~~~~~~~~~~

comma以外の区切り文字は ``delimiter`` で指定します。1文字だけ指定できます。

.. testcode:: csv-reader-delimiter

   import csv
   import io

   file = io.StringIO("a b c\n1 2 3\n")
   reader = csv.reader(file, delimiter=" ")
   assert list(reader) == [["a", "b", "c"], ["1", "2", "3"]]

単純な空白区切りで連続空白をまとめたいだけなら ``line.split()`` の方が自然です。
CSVとして引用符やdelimiterの規則がある場合に ``csv.reader`` を使います。

headerをkeyにする
~~~~~~~~~~~~~~~~~

``csv.DictReader`` は1行目をfield名として読み、各行をdictで返します。

.. testcode:: csv-dict-reader-header

   import csv
   import io

   file = io.StringIO("name,score\nAlice,90\nSmith, Bob,85\n")
   reader = csv.DictReader(file)
   rows = list(reader)
   assert rows[0] == {"name": "Alice", "score": "90"}

   # commaを含むfieldはCSV側で引用する。
   quoted_file = io.StringIO('name,score\n"Smith, Bob",85\n')
   quoted_row = next(csv.DictReader(quoted_file))
   assert quoted_row == {"name": "Smith, Bob", "score": "85"}

最初の ``file`` の2行目はdelimiterが3個あるため、余った値が ``None`` keyへ入ります。
列数の不一致を自動でエラーにはしない点に注意してください。

headerがないCSV
~~~~~~~~~~~~~~~

1行目もデータなら ``fieldnames`` を明示します。この場合、先頭行はheaderとして
読み飛ばされません。

.. testcode:: csv-dict-reader-fieldnames

   import csv
   import io

   file = io.StringIO("1,2,3,4\n5,6,7,8\n")
   reader = csv.DictReader(file, fieldnames=["a", "b", "c", "d"])
   assert list(reader) == [
       {"a": "1", "b": "2", "c": "3", "d": "4"},
       {"a": "5", "b": "6", "c": "7", "d": "8"},
   ]

CSVへ書く
---------

list・tupleを書く
~~~~~~~~~~~~~~~~~

``writerow`` は1行、``writerows`` は複数行を書きます。

.. testcode:: csv-writer-basic

   import csv
   import io

   file = io.StringIO(newline="")
   writer = csv.writer(file, lineterminator="\n")
   writer.writerow([0, 1, 2])
   writer.writerow(["a", "b", "c"])

   rows = [[3, 4, 5], ["x", "y", "z"]]
   writer.writerows(rows)
   assert file.getvalue() == "0,1,2\na,b,c\n3,4,5\nx,y,z\n"

実fileでは次の形です。``lineterminator`` は出力の改行を明示したい場合に指定します。

.. code-block:: python

   with open("output.csv", "w", encoding="utf-8", newline="") as file:
       writer = csv.writer(file)
       writer.writerow([0, 1, 2])
       writer.writerows(rows)

dictを書く
~~~~~~~~~~

``csv.DictWriter`` では列順を ``fieldnames`` で指定します。headerは自動ではなく
``writeheader`` で明示的に出力します。

.. testcode:: csv-dict-writer

   import csv
   import io

   d1 = {"a": 1, "b": 2, "c": 3}
   d2 = {"a": 4, "b": 5, "c": 6}

   file = io.StringIO(newline="")
   writer = csv.DictWriter(
       file,
       fieldnames=["a", "b", "c"],
       lineterminator="\n",
   )
   writer.writeheader()
   writer.writerow(d1)
   writer.writerow(d2)
   assert file.getvalue() == "a,b,c\n1,2,3\n4,5,6\n"

dictに ``fieldnames`` 以外のkeyがあると既定では ``ValueError`` です。欠けているkeyは
空fieldとして出力されます。必要なら ``extrasaction="ignore"`` や ``restval`` を
問題仕様に合わせて指定します。

CSVの注意点
-----------

* readerが返すfieldは基本的にstrです。整数などは明示的に変換します。
* ``split(",")`` では引用符内のcommaや改行を正しく処理できません。
* fileは ``newline=""`` で開き、改行処理を :mod:`csv` に任せます。
* delimiter、quote、headerの有無、encodingを入力仕様と合わせます。
* Excel向けUTF-8でBOMが付くfileを読む場合は ``encoding="utf-8-sig"`` を検討します。

JSONを読む・書く
----------------

JSONのobject、array、number、string、boolean、nullは主にPythonのdict、list、
int/float、str、bool、``None`` へ変換されます。

.. testcode:: json-file-basic

   import json
   from pathlib import Path
   from tempfile import TemporaryDirectory

   data = {"name": "東京", "values": [10, 20, 30], "enabled": True}
   with TemporaryDirectory() as temporary_directory:
       path = Path(temporary_directory) / "data.json"
       with path.open("w", encoding="utf-8") as file:
           json.dump(data, file, ensure_ascii=False, indent=2)
       with path.open("r", encoding="utf-8") as file:
           loaded = json.load(file)
       assert loaded == data

``json.load(file)`` はfileから、``json.loads(text)`` はstrから読みます。書き込み側は
``dump`` と ``dumps`` です。JSONはtuple、set、Decimalなどをそのまま保存する形式
ではありません。

.. seealso::

   :doc:`data_io` — 入出力ガイドの目次へ戻る。

   :doc:`file_io` — 通常のテキスト・binaryファイル。
