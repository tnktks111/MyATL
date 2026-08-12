SuccessorDSU
============

削除されていない次の位置を管理します。使い分けと例は
:doc:`../guides/union_find` を参照してください。

使いどころ
----------

位置を一度ずつ削除しながら「x以上でまだ残っている最小位置」を探す問題に使います。
削除の取り消しや、直前の生存位置の検索は扱えません。

完全例
------

削除、重複削除、successor query、番兵 ``n`` の扱いを含む例です。

.. testcode:: successor-dsu-complete

   from modified_union_find.successor_dsu import SuccessorDSU

   n = 5
   successor = SuccessorDSU(n)

   assert successor.next(0) == 0
   assert successor.erase(2)
   assert successor.erase(3)
   assert successor.next(2) == 4

   # 重複削除はFalseを返す。
   assert not successor.erase(2)

   assert successor.erase(4)
   assert successor.next(2) == n
   assert successor.next(n) == n

   print(successor.next(0))
   print(successor.next(2))

.. testoutput:: successor-dsu-complete

   0
   5

API仕様
-------

.. currentmodule:: modified_union_find.successor_dsu

.. autoclass:: SuccessorDSU
   :members:
   :member-order: bysource
   :show-inheritance:
