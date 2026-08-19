n進数・基数変換
===============

整数の値と、2進数・8進数・16進数などの文字列表現を相互変換します。Pythonの整数は
内部では任意精度の数値として扱われ、``"1010"`` や ``"ff"`` のような表記文字列と
区別されます。

2進数・8進数・16進数へ変換する
---------------------------------

``bin``、``oct``、``hex`` はprefix付きの文字列を返します。

.. testcode:: number-bases-builtins

   assert bin(10) == "0b1010"
   assert oct(10) == "0o12"
   assert hex(255) == "0xff"
   assert hex(255).upper() == "0XFF"

返り値は整数ではなくstrです。prefixなしの表記、幅指定、英字の大小を制御する場合は
``format`` またはf-stringを使います。

format指定
----------

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - 指定
     - 意味
     - ``value = 42`` の例
   * - ``b``
     - 2進数
     - ``101010``
   * - ``o``
     - 8進数
     - ``52``
   * - ``d``
     - 10進数
     - ``42``
   * - ``x``
     - 16進数・小文字
     - ``2a``
   * - ``X``
     - 16進数・大文字
     - ``2A``
   * - ``#b``, ``#o``, ``#x``
     - prefix付き
     - ``0b101010`` など

.. testcode:: number-bases-format

   value = 42
   assert format(value, "b") == "101010"
   assert format(value, "o") == "52"
   assert format(value, "x") == "2a"
   assert format(value, "X") == "2A"
   assert format(value, "#b") == "0b101010"
   assert f"{value:b}" == "101010"
   assert f"{value:#06x}" == "0x002a"

ゼロ埋めと桁数
--------------

幅の前に ``0`` を付けるとゼロ埋めします。幅にはsignとprefixも含まれます。

.. testcode:: number-bases-padding

   assert format(10, "08b") == "00001010"
   assert f"{10:04x}" == "000a"
   assert f"{10:#010b}" == "0b00001010"
   assert format(-10, "08b") == "-0001010"  # signも幅に含む

   bits = format(10, "b")
   assert len(bits) == 4
   assert (10).bit_length() == 4

``str.zfill`` でもsignを考慮したゼロ埋めができますが、進数変換と幅指定を同時に行う
場合はformat指定の方が明確です。

文字列から整数へ変換する
------------------------

``int(text, base)`` の ``base`` には2〜36を指定できます。英字は大文字・小文字を
区別せず、10〜35を ``a``〜``z`` で表します。

.. testcode:: number-bases-parse

   assert int("1010", 2) == 10
   assert int("12", 8) == 10
   assert int("42", 10) == 42
   assert int("ff", 16) == 255
   assert int("FF", 16) == 255
   assert int("z", 36) == 35
   assert int("-1010", 2) == -10
   assert int("ff_ff", 16) == 65535  # 数字間のunderscoreを許す

指定基数で使えないdigitが含まれると ``ValueError`` です。例えば ``int("2", 2)`` は
変換できません。

prefixから基数を自動判定する
----------------------------

``base=0`` はPython形式のprefixを見て基数を選びます。

.. testcode:: number-bases-auto-base

   assert int("0b1010", 0) == 10
   assert int("0o12", 0) == 10
   assert int("42", 0) == 42
   assert int("0xff", 0) == 255
   assert int("-0x10", 0) == -16

``base=0`` ではprefixのない ``"010"`` を8進数とは解釈しません。8進数なら
``"0o10"``、または ``int("10", 8)`` と明示します。

2〜36進数の文字列へ変換する
---------------------------

NumPyが利用できる環境では :func:`numpy.base_repr` が最短です。2〜36進数に対応し、
英字digitは大文字で返します。

.. testcode:: number-bases-numpy

   import numpy as np

   assert np.base_repr(10, base=2) == "1010"
   assert np.base_repr(10, base=3) == "101"
   assert np.base_repr(255, base=16) == "FF"
   assert np.base_repr(35, base=36) == "Z"
   assert np.base_repr(-10, base=3) == "-101"
   assert int(np.base_repr(1000, base=7), 7) == 1000

``padding`` は「全体の幅」ではなく、signの後へ追加するゼロの個数です。

.. testcode:: number-bases-numpy-padding

   import numpy as np

   assert np.base_repr(10, base=2, padding=4) == "00001010"
   assert np.base_repr(-10, base=2, padding=4) == "-00001010"

NumPyを持ち込めない環境や変換規則を変更したい場合は、基数で割った余りを末尾から
並べる次の標準Python実装を使います。

.. testcode:: number-bases-encode

   DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"

   def to_base(value: int, base: int) -> str:
       if not 2 <= base <= len(DIGITS):
           raise ValueError("base must be between 2 and 36")
       if value == 0:
           return "0"
       sign = "-" if value < 0 else ""
       value = abs(value)
       result = []
       while value:
           value, remainder = divmod(value, base)
           result.append(DIGITS[remainder])
       return sign + "".join(reversed(result))

   assert to_base(10, 2) == "1010"
   assert to_base(10, 3) == "101"
   assert to_base(255, 16) == "ff"
   assert to_base(35, 36) == "z"
   assert to_base(-10, 3) == "-101"
   assert to_base(0, 7) == "0"

2〜36進数から整数への逆変換は標準の ``int`` で十分です。

.. testcode:: number-bases-encode

   for base in range(2, 37):
       for value in (-1000, -1, 0, 1, 1000):
           assert int(to_base(value, base), base) == value

digitを1桁ずつ処理する
----------------------

文字列を左から読み、``value = value * base + digit`` とすると自前で復元できます。
桁DPや文字ごとの検査をするときの基本形です。

.. testcode:: number-bases-manual-parse

   DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"
   DIGIT_VALUE = {char: value for value, char in enumerate(DIGITS)}

   def from_base(text: str, base: int) -> int:
       if not 2 <= base <= 36:
           raise ValueError("base must be between 2 and 36")
       if not text:
           raise ValueError("text must not be empty")
       sign = -1 if text.startswith("-") else 1
       digits = text[1:] if text[:1] in "+-" else text
       if not digits:
           raise ValueError("digits must not be empty")
       value = 0
       for char in digits.lower():
           digit = DIGIT_VALUE.get(char, base)
           if digit >= base:
               raise ValueError("invalid digit")
           value = value * base + digit
       return sign * value

   assert from_base("1010", 2) == 10
   assert from_base("101", 3) == 10
   assert from_base("FF", 16) == 255
   assert from_base("-z", 36) == -35

固定幅2進数と2の補数
--------------------

``format(-1, "08b")`` は ``-0000001`` であり、8-bitの2の補数表現ではありません。
下位 ``width`` bitをmaskすると、固定幅のbit patternを得られます。

.. testcode:: number-bases-twos-complement

   def to_twos_complement(value: int, width: int) -> str:
       if width <= 0:
           raise ValueError("width must be positive")
       mask = (1 << width) - 1
       return format(value & mask, f"0{width}b")

   assert to_twos_complement(5, 8) == "00000101"
   assert to_twos_complement(-1, 8) == "11111111"
   assert to_twos_complement(-2, 8) == "11111110"

符号付き値へ戻すには最上位bitを確認します。

.. testcode:: number-bases-from-twos-complement

   def from_twos_complement(bits: str) -> int:
       if not bits or any(bit not in "01" for bit in bits):
           raise ValueError("bits must be a non-empty binary string")
       value = int(bits, 2)
       if bits[0] == "1":
           value -= 1 << len(bits)
       return value

   assert from_twos_complement("00000101") == 5
   assert from_twos_complement("11111111") == -1
   assert from_twos_complement("11111110") == -2

よくある間違い
--------------

* ``bin``、``oct``、``hex`` の返り値はstrです。
* ``int("1010")`` は10進数の1010です。2進数なら ``int("1010", 2)`` とします。
* ``int(text, 0)`` の自動判定には ``0b``、``0o``、``0x`` prefixが必要です。
* ``format`` の幅にはsignとprefixが含まれます。
* 負数の通常表記と、固定幅の2の補数bit patternを混同しません。
* 小数部分を含む任意基数変換は丸めと精度の設計が別途必要です。
* 36進数を超える場合はdigit集合と大小文字の扱いを独自に定義します。
* ``np.base_repr`` の ``padding`` は最終的な文字列幅ではなく追加ゼロ数です。
