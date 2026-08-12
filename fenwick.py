r"""Fenwick Tree (Binary Indexed Tree)。

0-indexed 配列の1点加算と半開区間 ``[left, right)`` の和を扱う。
構築は :math:`O(N)`、各操作は :math:`O(\log N)`、空間は
:math:`O(N)` である。境界探索には全要素が非負という前提がある。
"""


class FenwickTree:
    """1点加算・区間和用の Fenwick Tree。

    Args:
        n: 配列長。0も許す。
    """

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n must be non-negative")
        self._n = n
        self._data = [0] * n
    
    def add(self, index: int, value: int) -> None:
        """``a[index] += value`` を行う。"""
        if not 0 <= index < self._n:
            raise IndexError("index out of range")
        index += 1
        while index <= self._n:
            self._data[index - 1] += value
            index += index & -index
    
    def sum(self, left: int, right: int) -> int:
        """半開区間 ``[left, right)`` の和を返す。空区間は0。"""
        if not 0 <= left <= right <= self._n:
            raise IndexError("invalid half-open interval")
        return self._prefix_sum(right) - self._prefix_sum(left)
    
    def _prefix_sum(self, right: int) -> int:
        result = 0
        while right > 0:
            result += self._data[right - 1]
            right -= right & -right
        return result
    
    def lower_bound(self, target: int) -> int:
        r"""累積和が ``target`` 以上になる最初の要素位置を返す。

        全要素が非負であることが前提。該当要素がなければ ``n``、
        ``target <= 0`` なら0を返す。計算量は :math:`O(\log N)`。
        """
        if target <= 0:
            return 0
        index = 0
        bit = 1 << (self._n.bit_length() - 1) if self._n else 0
        while bit > 0:
            if (index + bit <= self._n
                    and self._data[index + bit - 1] < target):
                target -= self._data[index + bit - 1]
                index += bit
            bit >>= 1
        return index
    
    def upper_bound(self, target: int) -> int:
        r"""累積和が ``target`` より大きくなる最初の要素位置を返す。

        全要素が非負であることが前提。該当要素がなければ ``n``、
        ``target < 0`` なら0を返す。計算量は :math:`O(\log N)`。
        """
        if target < 0:
            return 0
        index = 0
        bit = 1 << (self._n.bit_length() - 1) if self._n else 0
        while bit > 0:
            if (index + bit <= self._n
                    and self._data[index + bit - 1] <= target):
                target -= self._data[index + bit - 1]
                index += bit
            bit >>= 1
        return index
__all__ = ["FenwickTree"]
