RollingHash
===========

部分文字列を確率的に高速比較します。使い分けと例は
:doc:`../guides/strings` を参照してください。

使いどころ
----------

文字列を一度前処理し、多数の部分文字列比較を行う場合に使います。異なる
インスタンス間でも比較できますが、確率的衝突を許せない用途には使えません。

完全例
------

同一文字列内と異なるインスタンス間の部分文字列比較、空区間を含む例です。

.. testcode:: rolling-hash-complete

   from rolling_hash import RollingHash

   text = RollingHash("abracadabra")
   pattern = RollingHash("abra")

   assert len(text) == 11
   assert text.get(0, 4) == text.get(7, 11)
   assert text.same(0, 4, pattern, 0, 4)
   assert not text.same(3, 7, pattern, 0, 4)
   assert not text.same(0, 3, pattern, 0, 4)  # 長さが違う
   assert text.same(5, 5, pattern, 2, 2)       # 空文字列同士

   print(text.same(0, 4, text, 7, 11))
   print(text.same(0, 4, pattern, 0, 4))

.. testoutput:: rolling-hash-complete

   True
   True

長さ確認を含む比較には ``same`` を使います。ハッシュ値はランダム基数に依存するため、
保存したり別プロセスへ渡したりしません。

API仕様
-------

.. currentmodule:: rolling_hash

.. autoclass:: RollingHash
   :members:
   :special-members: __len__
   :member-order: bysource
   :show-inheritance:
