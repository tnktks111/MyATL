Trie
====

重複を持たない文字列集合を管理します。使い分けと例は
:doc:`../guides/strings` を参照してください。

使いどころ
----------

文字列の追加・完全一致検索・削除・辞書順列挙を、文字列長に比例する時間で行いたい
場合に使います。この実装は出現回数やprefix件数を保持しません。

完全例
------

空文字、追加、重複追加、完全一致検索、削除、辞書順列挙を含む例です。

.. testcode:: trie-complete

   from trie import Trie

   trie = Trie()
   assert trie.insert("")
   assert trie.insert("cat")
   assert trie.insert("car")
   assert trie.insert("catalog")
   assert not trie.insert("cat")  # 集合なので重複しない

   assert trie.search("")
   assert trie.search("cat")
   assert not trie.search("ca")   # prefixだけでは完全一致しない
   assert len(trie) == 4
   assert trie.words() == ["", "car", "cat", "catalog"]

   assert trie.delete("cat")
   assert not trie.delete("cat")  # すでに存在しない
   assert not trie.delete("dog")
   assert trie.search("catalog")  # 長い語は残る

   print(trie.words())

.. testoutput:: trie-complete

   ['', 'car', 'catalog']

API仕様
-------

.. currentmodule:: trie

.. autoclass:: Trie
   :members:
   :special-members: __len__
   :member-order: bysource
   :show-inheritance:
