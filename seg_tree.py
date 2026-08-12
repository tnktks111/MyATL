"""モノイドの1点更新と半開区間積を扱う Segment Tree。"""

from collections.abc import Callable, Sequence
from typing import Any


def _ceil_pow2(n: int) -> int:
    return (n - 1).bit_length() if n else 0


class SegTree:
    r"""0-indexed の Segment Tree。

    ``op`` は結合的で、``e`` は左右の単位元でなければならない。演算は
    左から右の順で適用されるため非可換でもよい。構築は :math:`O(N)`、
    ``set``、``prod``、``max_right``、``min_left`` は
    :math:`O(\log N)`、``get`` と ``all_prod`` は :math:`O(1)`。

    Args:
        op: モノイドの二項演算。
        e: 単位元。
        values: 初期列、または単位元で埋める配列長。

    Notes:
        区間は半開区間 ``[left, right)``。境界探索の述語は ``f(e)`` が真で、
        探索方向に単調でなければならない。値と単位元を演算内で破壊しないこと。
    """

    def __init__(
        self,
        op: Callable[[Any, Any], Any],
        e: Any,
        values: int | Sequence[Any],
    ) -> None:
        self._op = op
        self._e = e
        if isinstance(values, int):
            if values < 0:
                raise ValueError("length must be non-negative")
            initial = [e] * values
        else:
            initial = list(values)
        self._n = len(initial)
        self._log = _ceil_pow2(self._n)
        self._size = 1 << self._log
        self._data = [e] * (2 * self._size)
        self._data[self._size:self._size + self._n] = initial
        for node in range(self._size - 1, 0, -1):
            self._update(node)

    def set(self, index: int, value: Any) -> None:
        """``a[index] = value`` を行う。"""
        if not 0 <= index < self._n:
            raise IndexError("index out of range")
        node = index + self._size
        self._data[node] = value
        for level in range(1, self._log + 1):
            self._update(node >> level)

    def get(self, index: int) -> Any:
        """``a[index]`` を返す。"""
        if not 0 <= index < self._n:
            raise IndexError("index out of range")
        return self._data[index + self._size]

    def prod(self, left: int, right: int) -> Any:
        """半開区間 ``[left, right)`` の積を返す。空区間は ``e``。"""
        if not 0 <= left <= right <= self._n:
            raise IndexError("invalid half-open interval")
        left += self._size
        right += self._size
        left_product = self._e
        right_product = self._e
        while left < right:
            if left & 1:
                left_product = self._op(left_product, self._data[left])
                left += 1
            if right & 1:
                right -= 1
                right_product = self._op(self._data[right], right_product)
            left >>= 1
            right >>= 1
        return self._op(left_product, right_product)

    def all_prod(self) -> Any:
        """全区間 ``[0, n)`` の積を返す。"""
        return self._data[1]

    def max_right(self, left: int, f: Callable[[Any], bool]) -> int:
        """``f(prod(left, right))`` が真となる最大の ``right`` を返す。"""
        if not 0 <= left <= self._n:
            raise IndexError("left out of range")
        if not f(self._e):
            raise ValueError("f(e) must be True")
        if left == self._n:
            return self._n
        node = left + self._size
        product = self._e
        while True:
            while node % 2 == 0:
                node >>= 1
            candidate = self._op(product, self._data[node])
            if not f(candidate):
                while node < self._size:
                    node *= 2
                    candidate = self._op(product, self._data[node])
                    if f(candidate):
                        product = candidate
                        node += 1
                return node - self._size
            product = candidate
            node += 1
            if (node & -node) == node:
                break
        return self._n

    def min_left(self, right: int, f: Callable[[Any], bool]) -> int:
        """``f(prod(left, right))`` が真となる最小の ``left`` を返す。"""
        if not 0 <= right <= self._n:
            raise IndexError("right out of range")
        if not f(self._e):
            raise ValueError("f(e) must be True")
        if right == 0:
            return 0
        node = right + self._size
        product = self._e
        while True:
            node -= 1
            while node > 1 and node % 2:
                node >>= 1
            candidate = self._op(self._data[node], product)
            if not f(candidate):
                while node < self._size:
                    node = 2 * node + 1
                    candidate = self._op(self._data[node], product)
                    if f(candidate):
                        product = candidate
                        node -= 1
                return node + 1 - self._size
            product = candidate
            if (node & -node) == node:
                break
        return 0

    def _update(self, node: int) -> None:
        self._data[node] = self._op(
            self._data[2 * node], self._data[2 * node + 1]
        )


__all__ = ["SegTree"]
