"""モノイド作用による区間更新を扱う Lazy Segment Tree。"""

from collections.abc import Callable, Sequence
from typing import Any


_MISSING = object()


def _ceil_pow2(n: int) -> int:
    return (n - 1).bit_length() if n else 0


class LazySegTree:
    r"""0-indexed、半開区間の Lazy Segment Tree。

    ``op`` と ``e`` はモノイド、``mapping(action, value)`` は作用、
    ``composition(new, old)`` は「oldの後にnew」を表す必要がある。つまり
    ``mapping(composition(f, g), x) == mapping(f, mapping(g, x))``。

    構築は :math:`O(N)`、``all_prod`` は :math:`O(1)`、その他の公開操作は
    :math:`O(\log N)`。値・作用・単位元をコールバック内で破壊しないこと。

    Args:
        op: 区間情報を左から右へ結合する演算。非可換でもよい。
        e: ``op`` の単位元。
        mapping: 作用を区間情報へ適用する関数。
        composition: 新旧の作用を合成する関数。
        identity: 何もしない作用。
        values: 初期列、または ``e`` で埋める配列長。
    """

    def __init__(
        self,
        op: Callable[[Any, Any], Any],
        e: Any,
        mapping: Callable[[Any, Any], Any],
        composition: Callable[[Any, Any], Any],
        identity: Any,
        values: int | Sequence[Any],
    ) -> None:
        self._op = op
        self._e = e
        self._mapping = mapping
        self._composition = composition
        self._identity = identity
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
        self._lazy = [identity] * self._size
        self._data[self._size:self._size + self._n] = initial
        for node in range(self._size - 1, 0, -1):
            self._update(node)

    def set(self, index: int, value: Any) -> None:
        """``a[index] = value`` を行う。"""
        if not 0 <= index < self._n:
            raise IndexError("index out of range")
        node = index + self._size
        for level in range(self._log, 0, -1):
            self._push(node >> level)
        self._data[node] = value
        for level in range(1, self._log + 1):
            self._update(node >> level)

    def get(self, index: int) -> Any:
        """``a[index]`` を返す。"""
        if not 0 <= index < self._n:
            raise IndexError("index out of range")
        node = index + self._size
        for level in range(self._log, 0, -1):
            self._push(node >> level)
        return self._data[node]

    def prod(self, left: int, right: int) -> Any:
        """半開区間 ``[left, right)`` の積を返す。空区間は ``e``。"""
        if not 0 <= left <= right <= self._n:
            raise IndexError("invalid half-open interval")
        if left == right:
            return self._e
        left += self._size
        right += self._size
        for level in range(self._log, 0, -1):
            if ((left >> level) << level) != left:
                self._push(left >> level)
            if ((right >> level) << level) != right:
                self._push((right - 1) >> level)
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

    def apply(self, left: int, right: Any = _MISSING, f: Any = _MISSING) -> None:
        """1点または半開区間へ作用を適用する。

        ``apply(index, action)`` または ``apply(index, f=action)`` は1点、
        ``apply(left, right, action)`` は区間更新。作用 ``None`` も使用できる。
        """
        if f is _MISSING:
            if right is _MISSING:
                raise TypeError("an action is required")
            index = left
            action = right
            if not 0 <= index < self._n:
                raise IndexError("index out of range")
            node = index + self._size
            for level in range(self._log, 0, -1):
                self._push(node >> level)
            self._data[node] = self._mapping(action, self._data[node])
            for level in range(1, self._log + 1):
                self._update(node >> level)
            return
        action = f
        if right is _MISSING:
            index = left
            if not 0 <= index < self._n:
                raise IndexError("index out of range")
            node = index + self._size
            for level in range(self._log, 0, -1):
                self._push(node >> level)
            self._data[node] = self._mapping(action, self._data[node])
            for level in range(1, self._log + 1):
                self._update(node >> level)
            return
        if not isinstance(right, int) or not 0 <= left <= right <= self._n:
            raise IndexError("invalid half-open interval")
        if left == right:
            return
        left += self._size
        right += self._size
        for level in range(self._log, 0, -1):
            if ((left >> level) << level) != left:
                self._push(left >> level)
            if ((right >> level) << level) != right:
                self._push((right - 1) >> level)
        original_left, original_right = left, right
        while left < right:
            if left & 1:
                self._all_apply(left, action)
                left += 1
            if right & 1:
                right -= 1
                self._all_apply(right, action)
            left >>= 1
            right >>= 1
        left, right = original_left, original_right
        for level in range(1, self._log + 1):
            if ((left >> level) << level) != left:
                self._update(left >> level)
            if ((right >> level) << level) != right:
                self._update((right - 1) >> level)

    def max_right(self, left: int, f: Callable[[Any], bool]) -> int:
        """``f(prod(left, right))`` が真となる最大の ``right`` を返す。"""
        if not 0 <= left <= self._n:
            raise IndexError("left out of range")
        if not f(self._e):
            raise ValueError("f(e) must be True")
        if left == self._n:
            return self._n
        node = left + self._size
        for level in range(self._log, 0, -1):
            self._push(node >> level)
        product = self._e
        while True:
            while node % 2 == 0:
                node >>= 1
            candidate = self._op(product, self._data[node])
            if not f(candidate):
                while node < self._size:
                    self._push(node)
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
        for level in range(self._log, 0, -1):
            self._push((node - 1) >> level)
        product = self._e
        while True:
            node -= 1
            while node > 1 and node % 2:
                node >>= 1
            candidate = self._op(self._data[node], product)
            if not f(candidate):
                while node < self._size:
                    self._push(node)
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

    def _all_apply(self, node: int, action: Any) -> None:
        self._data[node] = self._mapping(action, self._data[node])
        if node < self._size:
            self._lazy[node] = self._composition(action, self._lazy[node])

    def _push(self, node: int) -> None:
        self._all_apply(2 * node, self._lazy[node])
        self._all_apply(2 * node + 1, self._lazy[node])
        self._lazy[node] = self._identity


__all__ = ["LazySegTree"]
