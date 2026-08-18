文字列アルゴリズムガイド
========================

Python標準の文字列操作
----------------------

文字列 ``str`` は変更不能（immutable）です。メソッドは元の文字列を変更せず、必要に
応じて新しい文字列を返します。

.. testcode:: guide-string-basic

   text = "algorithm"
   assert len(text) == 9
   assert text[0] == "a"
   assert text[-1] == "m"
   assert text[1:4] == "lgo"       # [start, stop)
   assert text[::2] == "agrtm"     # 1文字おき
   assert text[::-1] == "mhtirogla" # 反転
   assert "algo" in text

検索・個数・prefix/suffix
~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 28 38 34

   * - 操作
     - 意味
     - 見つからない場合
   * - ``sub in s``
     - 部分文字列を含むか
     - ``False``
   * - ``s.find(sub)``
     - 最初の開始位置
     - ``-1``
   * - ``s.rfind(sub)``
     - 最後の開始位置
     - ``-1``
   * - ``s.index(sub)``
     - 最初の開始位置
     - ``ValueError``
   * - ``s.count(sub)``
     - 重ならない出現回数
     - ``0``
   * - ``s.startswith(prefix)``
     - prefixで始まるか
     - ``False``
   * - ``s.endswith(suffix)``
     - suffixで終わるか
     - ``False``

.. testcode:: guide-string-search

   text = "banana"
   assert text.find("an") == 1
   assert text.rfind("an") == 3
   assert text.find("xy") == -1
   assert text.count("ana") == 1  # 重なる2箇所は数えない
   assert text.startswith(("ba", "ca"))  # tupleならいずれか
   assert text.endswith("na")
   assert text.find("a", 2, 5) == 3        # 検索範囲も[start, stop)

存在しないことが通常ケースなら ``find``、存在が前提で違反を例外にしたいなら
``index`` を使います。重なる出現を数える場合は ``find`` の開始位置を1ずつ進める
など、別の処理が必要です。

分割・結合
~~~~~~~~~~

.. testcode:: guide-string-split-join

   assert "  10  20\t30  ".split() == ["10", "20", "30"]
   assert "a,,b,".split(",") == ["a", "", "b", ""]
   assert "a,b,c".split(",", maxsplit=1) == ["a", "b,c"]
   assert "a,b,c".rsplit(",", maxsplit=1) == ["a,b", "c"]
   assert "key=value=rest".partition("=") == ("key", "=", "value=rest")
   assert "\n".join(["red", "blue"]) == "red\nblue"
   assert "a\r\nb\nc".splitlines() == ["a", "b", "c"]

``split()`` は連続する空白文字をまとめ、先頭・末尾の空白も無視します。一方、
``split(" ")`` は半角スペース1文字を区切りとして空要素も残します。標準入力を
空白区切りで読む場合は通常 ``split()`` を使います。``join`` は区切り文字側の
メソッドで、要素は文字列でなければなりません。

除去・置換
~~~~~~~~~~

.. testcode:: guide-string-strip-replace

   assert "  hello\n".strip() == "hello"
   assert "--value--".strip("-") == "value"
   assert "xyvalueyx".strip("xy") == "value"
   assert "prefix_value".removeprefix("prefix_") == "value"
   assert "file.txt".removesuffix(".txt") == "file"
   assert "a-b-c".replace("-", ":") == "a:b:c"
   assert "a-b-c".replace("-", ":", 1) == "a:b-c"

``strip(chars)`` の引数は部分文字列ではなく「除去してよい文字の集合」です。
決まったprefix/suffixを1回だけ除去する場合は ``removeprefix`` /
``removesuffix`` を使います。左側だけなら ``lstrip``、右側だけなら ``rstrip`` です。

大文字・小文字と文字種判定
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - メソッド
     - 判定・変換
   * - ``lower()``, ``upper()``
     - 小文字化、大文字化
   * - ``swapcase()``
     - 大文字と小文字を交換
   * - ``capitalize()``, ``title()``
     - 先頭、または各単語の先頭を大文字化
   * - ``isalpha()``
     - 1文字以上で、すべて文字
   * - ``isdigit()``
     - 1文字以上で、すべて数字文字
   * - ``isalnum()``
     - 1文字以上で、すべて文字または数字
   * - ``islower()``, ``isupper()``
     - 大文字・小文字を持つ文字が条件を満たす
   * - ``isspace()``
     - 1文字以上で、すべて空白文字

.. testcode:: guide-string-character-kinds

   assert "PyThOn".lower() == "python"
   assert "PyThOn".swapcase() == "pYtHoN"
   assert "abc".isalpha()
   assert "123".isdigit()
   assert "abc123".isalnum()
   assert not "".isdigit()  # is...系は空文字にFalse
   char = "7"
   assert "0" <= char <= "9"  # ASCII数字だけに限定したい場合

``isalpha`` や ``isdigit`` はUnicode文字も対象です。競技問題でASCII英数字だけを
判定したい場合は ``"a" <= char <= "z"`` や ``"0" <= char <= "9"`` のように
範囲比較します。大文字小文字を無視したUnicode比較には ``casefold()`` もあります。

文字コード・整形・一括変換
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. testcode:: guide-string-code-format

   assert ord("a") == 97
   assert chr(97) == "a"
   assert chr(ord("c") + 2) == "e"
   assert "42".zfill(5) == "00042"
   assert "x".ljust(3, ".") == "x.."
   assert "x".rjust(3, ".") == "..x"

   table = str.maketrans({"A": "T", "T": "A", "C": "G", "G": "C"})
   assert "ACGT".translate(table) == "TGCA"

``ord`` は1文字を整数コードポイントへ、``chr`` は整数を1文字へ変換します。
複数種類の文字を同時置換する場合は、``replace`` の連鎖より ``translate`` が安全な
ことがあります。固定幅のゼロ埋めは ``zfill``、一般の表示整形にはf-stringも使えます。

よく使う組み合わせ
~~~~~~~~~~~~~~~~~~

.. testcode:: guide-string-recipes

   # 文字列を変更したいときはlistへ変換して戻す。
   chars = list("code")
   chars[0] = "m"
   assert "".join(chars) == "mode"

   # 文字の出現回数。
   from collections import Counter
   assert Counter("banana") == Counter({"a": 3, "n": 2, "b": 1})

   # 辞書順、長さ優先、反転。
   words = ["pear", "fig", "apple"]
   assert sorted(words) == ["apple", "fig", "pear"]
   assert sorted(words, key=lambda word: (len(word), word)) == [
       "fig", "pear", "apple"
   ]
   assert "".join(reversed("abc")) == "cba"

Trie
----

文字列集合への追加、完全一致検索、削除、辞書順列挙を行います。空文字も登録でき、
重複insertは集合と同じく1個として扱います。

.. testcode:: guide-trie

   from trie import Trie

   words = Trie()
   words.insert("cat")
   words.insert("car")
   assert words.search("cat")
   assert words.words() == ["car", "cat"]

この実装はprefix件数、出現回数、最長共通接頭辞を直接返しません。大量の静的文字列
だけを検索するならソート済み配列と二分探索の方が省メモリな場合があります。削除は
論理削除で、不要ノードを回収しません。

Rolling Hash
------------

文字列を一度 :math:`O(N)` で前処理し、部分文字列を期待 :math:`O(1)` で比較します。
異なるインスタンス間でも ``same`` を使用できます。

.. testcode:: guide-rolling-hash

   from rolling_hash import RollingHash

   text = RollingHash("abracadabra")
   pattern = RollingHash("abra")
   assert text.same(0, 4, pattern, 0, 4)

ハッシュ衝突の可能性はゼロではありません。厳密な一致証明が必要な問題では実文字列
比較、suffix arrayなどを検討します。基数はプロセスごとにランダムなので、ハッシュ
値の永続化や別プロセスとの交換には使えません。

API仕様
-------

:class:`trie.Trie`、:class:`rolling_hash.RollingHash` を参照してください。
