文字列アルゴリズムガイド
========================

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
