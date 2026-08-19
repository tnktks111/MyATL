binary入出力
============

binary modeではデータを :class:`bytes` としてそのまま読み書きします。独自formatや
固定長recordでは、byte order、符号、整数幅、浮動小数形式、文字encodingをfile仕様と
完全に合わせる必要があります。

text modeとの違い
-----------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - mode
     - 読み書きする型
     - 主な用途
   * - ``"r"``, ``"w"``
     - ``str``
     - encodingされたテキスト
   * - ``"rb"``, ``"wb"``
     - ``bytes``
     - binary format、画像、圧縮データ
   * - ``"ab"``
     - ``bytes``
     - binaryデータの末尾への追記

binary modeでは ``encoding`` と ``newline`` を指定しません。``write`` にstrを渡したり、
text modeでbytesを書いたりすると ``TypeError`` になります。

bytesの基本
-----------

``bytes`` は変更不能です。添字は長さ1のbytesではなく、0から255の整数を返します。

.. testcode:: binary-io-bytes-basic

   data = b"ABC\x00\xff"
   assert len(data) == 5
   assert data[0] == 65
   assert data[-1] == 255
   assert data[1:3] == b"BC"
   assert bytes([65, 66, 67]) == b"ABC"
   assert list(data[:3]) == [65, 66, 67]

変更可能なbyte列が必要なら :class:`bytearray` を使います。コピーせず参照したい場合は
:class:`memoryview` を検討します。

.. testcode:: binary-io-bytearray

   data = bytearray(b"ABC")
   data[1] = ord("x")
   data.extend(b"!")
   assert data == bytearray(b"AxC!")
   assert bytes(data) == b"AxC!"

file全体を読む・書く
--------------------

binary fileは ``with open(...) as f`` で開きます。``with`` blockを抜けると、例外が
発生した場合もfileが閉じられます。

.. testcode:: binary-io-whole-file

   import os
   from tempfile import TemporaryDirectory

   with TemporaryDirectory() as temporary_directory:
       file_path = os.path.join(temporary_directory, "data.bin")
       with open(file_path, "wb") as f:
           written = f.write(b"\x01\x02\xff")
       assert written == 3

       with open(file_path, "rb") as f:
           data = f.read()
       assert data == b"\x01\x02\xff"

巨大なfileは全体をメモリへ載せず、``open(path, "rb")`` でblockごとに読みます。

.. testcode:: binary-io-blocks

   import os
   from tempfile import TemporaryDirectory

   with TemporaryDirectory() as temporary_directory:
       file_path = os.path.join(temporary_directory, "blocks.bin")
       with open(file_path, "wb") as f:
           f.write(b"abcdefghij")

       blocks = []
       with open(file_path, "rb") as f:
           while block := f.read(4):
               blocks.append(block)
       assert blocks == [b"abcd", b"efgh", b"ij"]

``read(size)`` はEOF付近で ``size`` より短いbytesを返し、EOF後は ``b""`` を返します。
1回の ``read(size)`` が常に指定sizeを返すとは仮定しません。

整数とbytesの変換
-----------------

整数1個なら ``int.to_bytes`` と ``int.from_bytes`` が使えます。

.. testcode:: binary-io-integer

   value = 0x12345678
   little = value.to_bytes(4, byteorder="little", signed=False)
   big = value.to_bytes(4, byteorder="big", signed=False)
   assert little == b"\x78\x56\x34\x12"
   assert big == b"\x12\x34\x56\x78"
   assert int.from_bytes(little, "little", signed=False) == value
   assert int.from_bytes(big, "big", signed=False) == value

   negative = (-2).to_bytes(2, "little", signed=True)
   assert negative == b"\xfe\xff"
   assert int.from_bytes(negative, "little", signed=True) == -2

指定byte数に収まらない値や、``signed=False`` で負数を変換すると ``OverflowError``
です。formatに可変長整数が定義されている場合は、その仕様どおりのencode/decodeが
別途必要です。

structのformat
--------------

:mod:`struct` は複数の固定幅値をまとめてpack/unpackします。format文字列の先頭で
byte orderとalignmentを指定します。

.. list-table:: byte order prefix
   :header-rows: 1
   :widths: 20 40 40

   * - prefix
     - byte order
     - size・alignment
   * - ``<``
     - little endian
     - 標準size、paddingなし
   * - ``>`` / ``!``
     - big endian / network order
     - 標準size、paddingなし
   * - ``=``
     - native byte order
     - 標準size、paddingなし
   * - ``@``
     - native
     - native size・alignment

portableなfile formatでは通常 ``<`` または ``>`` を明示します。

.. list-table:: よく使うformat文字
   :header-rows: 1
   :widths: 18 42 40

   * - 文字
     - Python側
     - 標準size
   * - ``b`` / ``B``
     - signed / unsigned整数
     - 1 byte
   * - ``h`` / ``H``
     - signed / unsigned整数
     - 2 bytes
   * - ``i`` / ``I``
     - signed / unsigned整数
     - 4 bytes
   * - ``q`` / ``Q``
     - signed / unsigned整数
     - 8 bytes
   * - ``f`` / ``d``
     - 浮動小数
     - 4 / 8 bytes
   * - ``?``
     - bool
     - 1 byte
   * - ``Ns``
     - 長さNのbytes
     - N bytes
   * - ``x``
     - padding
     - 1 byte

固定長recordをpack/unpackする
-----------------------------

同じformatを繰り返し使うなら ``struct.Struct`` を作ります。``<Ih`` はlittle endianの
unsigned 32-bit整数とsigned 16-bit整数です。

.. testcode:: binary-io-struct-record

   import struct

   record_format = struct.Struct("<Ih")
   raw = record_format.pack(100_000, -123)
   assert raw == b"\xa0\x86\x01\x00\x85\xff"
   assert record_format.size == 6
   assert struct.calcsize("<Ih") == 6
   identifier, delta = record_format.unpack(raw)
   assert (identifier, delta) == (100_000, -123)

``unpack`` は入力長がformat sizeと完全一致しないと ``struct.error`` になります。

固定長recordを順に読む
----------------------

.. testcode:: binary-io-fixed-records

   import os
   import struct
   from tempfile import TemporaryDirectory

   record_format = struct.Struct(">Hh")
   with TemporaryDirectory() as temporary_directory:
       file_path = os.path.join(temporary_directory, "records.bin")
       with open(file_path, "wb") as f:
           f.write(record_format.pack(1, -10))
           f.write(record_format.pack(2, 20))

       records = []
       with open(file_path, "rb") as f:
           while True:
               chunk = f.read(record_format.size)
               if not chunk:
                   break
               if len(chunk) != record_format.size:
                   raise EOFError("incomplete record")
               records.append(record_format.unpack(chunk))
       assert records == [(1, -10), (2, 20)]

すでに全体がbytesとしてある場合は ``iter_unpack`` が簡潔です。全体長はrecord sizeの
倍数でなければなりません。

.. testcode:: binary-io-iter-unpack

   import struct

   raw = struct.pack("<3I", 10, 20, 30)
   assert list(struct.iter_unpack("<I", raw)) == [(10,), (20,), (30,)]

offsetを指定して読む・書く
--------------------------

``unpack_from`` / ``pack_into`` はbuffer内のoffsetを指定します。``pack_into`` のbufferは
``bytearray`` など変更可能な必要があります。

.. testcode:: binary-io-offset

   import struct

   buffer = bytearray(12)
   struct.pack_into("<I", buffer, 4, 0x12345678)
   assert struct.unpack_from("<I", buffer, 4) == (0x12345678,)
   assert buffer[4:8] == b"\x78\x56\x34\x12"

seekとtell
----------

``tell`` は現在位置、``seek`` は位置を変更します。基準は先頭 ``SEEK_SET``、現在位置
``SEEK_CUR``、末尾 ``SEEK_END`` です。

.. testcode:: binary-io-seek

   import os
   from tempfile import TemporaryDirectory

   with TemporaryDirectory() as temporary_directory:
       file_path = os.path.join(temporary_directory, "seek.bin")
       with open(file_path, "wb") as f:
           f.write(b"0123456789")

       with open(file_path, "rb") as f:
           f.seek(4)
           assert f.tell() == 4
           assert f.read(3) == b"456"
           f.seek(-2, os.SEEK_END)
           assert f.read() == b"89"

text modeではencodingや改行変換があるため任意byte offsetへのseekを考えない方が安全
です。binary modeではformatが定めるoffsetをそのまま扱えます。

文字列を格納する場合
--------------------

strをbinaryへ入れるにはencodingを明示します。固定長fieldではbyte長と文字数が一致
しないことに注意します。

.. testcode:: binary-io-text-encoding

   text = "東京"
   encoded = text.encode("utf-8")
   assert len(text) == 2
   assert len(encoded) == 6
   assert encoded.decode("utf-8") == text

終端NUL、長さprefix、固定長paddingなど、文字列の境界はformat仕様に従います。任意の
位置でmulti-byte文字を切るとdecodeできません。

注意点
------

* endian、signed/unsigned、幅、alignmentを推測せず仕様で確認します。
* 不完全recordを正常なEOFと混同しません。
* 浮動小数のbinary表現にも丸め誤差があります。
* 信頼できないfileの長さ値を、そのまま巨大なメモリ確保へ使いません。
* 画像、圧縮、音声など既存formatは対応する標準module・libraryで処理します。
* binaryデータをtextとして無理にdecodeしません。

.. seealso::

   :doc:`data_io` — 入出力ガイドの目次へ戻る。

   :doc:`file_io` — Pathと通常のテキストファイル。
