"""
遅延セグメント木。
区間はすべて半開区間 [l, r) として扱う。
Parameters
----------
op : Callable[[S, S], S]
    2つの区間情報を結合する演算。
e : S
    op の単位元。
mapping : Callable[[F, S], S]
    更新操作 f を区間情報 x に作用させる関数。
composition : Callable[[F, F], F]
    更新操作を合成する関数。

    composition(f, g) は、
    「先に g を適用し、その後に f を適用する操作」を返す。

    次を満たす必要がある。

        mapping(composition(f, g), x)
        == mapping(f, mapping(g, x))

id_ : F
    何もしない更新操作。
v : int | list[S]
    初期配列。整数の場合は、長さ v の e で初期化する。

主な操作
--------
set(p, x)
    A[p] を x に変更する。O(log N)

get(p)
    A[p] を取得する。O(log N)

prod(l, r)
    区間 [l, r) の集約値を取得する。O(log N)

all_prod()
    全区間の集約値を取得する。O(1)

apply(l, r, f)
    区間 [l, r) に更新操作 f を適用する。O(log N)

apply(p, f=f)
    位置 p に更新操作 f を適用する。O(log N)

max_right(l, g)
    g(prod(l, r)) が真となる最大の r を求める。O(log N)

min_left(r, g)
    g(prod(l, r)) が真となる最小の l を求める。O(log N)


設計例1: 区間加算・区間最小値
--------------------------------
各区間に最小値を保存し、区間全体に一定値を加算する。

    S = int
    F = int

    INF = float("inf")

    def op(a, b):
        return min(a, b)

    e = INF

    def mapping(f, x):
        return x + f

    def composition(f, g):
        return f + g

    id_ = 0

    seg = LazySegTree(
        op,
        e,
        mapping,
        composition,
        id_,
        A,
    )

    # [l, r) に x を加算
    seg.apply(l, r, x)

    # [l, r) の最小値
    answer = seg.prod(l, r)


設計例2: 区間加算・区間和
--------------------------
区間和を更新するには区間長が必要なので、
各ノードに (区間和, 区間長) を保存する。

    S = tuple[int, int]  # (区間和, 区間長)
    F = int              # 加算値

    def op(a, b):
        return (
            a[0] + b[0],
            a[1] + b[1],
        )

    e = (0, 0)

    def mapping(f, x):
        total, length = x
        return (
            total + f * length,
            length,
        )

    def composition(f, g):
        return f + g

    id_ = 0

    initial = [(x, 1) for x in A]

    seg = LazySegTree(
        op,
        e,
        mapping,
        composition,
        id_,
        initial,
    )

    # [l, r) に x を加算
    seg.apply(l, r, x)

    # [l, r) の和
    answer = seg.prod(l, r)[0]


設計例3: 区間代入・区間最小値
------------------------------
None を「何もしない操作」、
整数 x を「区間全体を x に変更する操作」とする。

    S = int
    F = int | None

    INF = float("inf")

    def op(a, b):
        return min(a, b)

    e = INF

    def mapping(f, x):
        if f is None:
            return x
        return f

    def composition(f, g):
        # 先に g、その後に f を適用する。
        # 新しい代入 f があれば、古い代入 g は上書きされる。
        if f is None:
            return g
        return f

    id_ = None

    seg = LazySegTree(
        op,
        e,
        mapping,
        composition,
        id_,
        A,
    )

    # [l, r) の全要素を x に変更
    seg.apply(l, r, x)

    # [l, r) の最小値
    answer = seg.prod(l, r)


設計例4: 区間代入・区間和
--------------------------
各ノードに (区間和, 区間長) を保存する。

    S = tuple[int, int]  # (区間和, 区間長)
    F = int | None       # None または代入値

    def op(a, b):
        return (
            a[0] + b[0],
            a[1] + b[1],
        )

    e = (0, 0)

    def mapping(f, x):
        if f is None:
            return x

        _, length = x
        return (
            f * length,
            length,
        )

    def composition(f, g):
        if f is None:
            return g
        return f

    id_ = None

    initial = [(x, 1) for x in A]

    seg = LazySegTree(
        op,
        e,
        mapping,
        composition,
        id_,
        initial,
    )

    # [l, r) の全要素を x に変更
    seg.apply(l, r, x)

    # [l, r) の和
    answer = seg.prod(l, r)[0]


設計例5: 区間をすべて1に変更・0の個数
--------------------------------------
配列の値を 0 または 1 とする。

各ノードには、実際の値ではなく
「区間内に存在する0の個数」を保存する。

    S = int   # 0の個数
    F = bool  # True: すべて1にする

    def op(a, b):
        return a + b

    e = 0

    def mapping(f, x):
        if not f:
            return x

        # 区間をすべて1にすると、0の個数は0になる。
        return 0

    def composition(f, g):
        # 一度でも「すべて1にする」があれば、
        # 合成後も「すべて1にする」。
        return f or g

    id_ = False

    A = [0, 1, 0, 0, 1]

    initial = [
        1 if x == 0 else 0
        for x in A
    ]

    seg = LazySegTree(
        op,
        e,
        mapping,
        composition,
        id_,
        initial,
    )

    # [l, r) をすべて1に変更
    seg.apply(l, r, True)

    # [l, r) に存在する0の個数
    answer = seg.prod(l, r)


設計例6: 0と1の反転・1の個数
----------------------------
区間内の0と1を反転し、1の個数を取得する。

反転後の1の個数は、

    区間長 - 反転前の1の個数

となるため、各ノードに区間長も保存する。

    S = tuple[int, int]  # (1の個数, 区間長)
    F = bool             # True: 0と1を反転

    def op(a, b):
        return (
            a[0] + b[0],
            a[1] + b[1],
        )

    e = (0, 0)

    def mapping(f, x):
        ones, length = x

        if not f:
            return x

        return (
            length - ones,
            length,
        )

    def composition(f, g):
        # 反転を2回行うと元に戻る。
        return f ^ g

    id_ = False

    initial = [(x, 1) for x in A]

    seg = LazySegTree(
        op,
        e,
        mapping,
        composition,
        id_,
        initial,
    )

    # [l, r) の0と1を反転
    seg.apply(l, r, True)

    # [l, r) の1の個数
    answer = seg.prod(l, r)[0]


設計例7: 一次関数更新・区間和
------------------------------
区間内の各要素 x に対して、

    x <- a * x + b

を適用し、区間和を取得する。

各ノードに (区間和, 区間長) を保存する。

    S = tuple[int, int]  # (区間和, 区間長)
    F = tuple[int, int]  # (a, b)

    def op(x, y):
        return (
            x[0] + y[0],
            x[1] + y[1],
        )

    e = (0, 0)

    def mapping(f, x):
        a, b = f
        total, length = x

        return (
            a * total + b * length,
            length,
        )

    def composition(f, g):
        # 先に
        #     x <- g_a * x + g_b
        # を適用し、その後に
        #     x <- f_a * x + f_b
        # を適用する。
        f_a, f_b = f
        g_a, g_b = g

        return (
            f_a * g_a,
            f_a * g_b + f_b,
        )

    id_ = (1, 0)

    initial = [(x, 1) for x in A]

    seg = LazySegTree(
        op,
        e,
        mapping,
        composition,
        id_,
        initial,
    )

    # [l, r) の各要素を a*x+b に変更
    seg.apply(l, r, (a, b))

    # [l, r) の和
    answer = seg.prod(l, r)[0]


設計時に確認する条件
--------------------
1. op の単位元

    op(e, x) == x
    op(x, e) == x

2. 更新の恒等操作

    mapping(id_, x) == x

3. 更新操作の合成順序

    mapping(composition(f, g), x)
    == mapping(f, mapping(g, x))

4. 区間結合と更新の整合性

    mapping(f, op(x, y))
    == op(mapping(f, x), mapping(f, y))

区間和の更新で区間長が必要になる場合などは、
S に区間長を含めること。
"""

import typing

def _ceil_pow2(n: int) -> int:
    x = 0
    while (1 << x) < n:
        x += 1

    return x

class LazySegTree:
    def __init__(
            self,
            op: typing.Callable[[typing.Any, typing.Any], typing.Any],
            e: typing.Any,
            mapping: typing.Callable[[typing.Any, typing.Any], typing.Any],
            composition: typing.Callable[[typing.Any, typing.Any], typing.Any],
            id_: typing.Any,
            v: typing.Union[int, typing.List[typing.Any]]) -> None:
        self._op = op
        self._e = e
        self._mapping = mapping
        self._composition = composition
        self._id = id_

        if isinstance(v, int):
            v = [e] * v

        self._n = len(v)
        self._log = _ceil_pow2(self._n)
        self._size = 1 << self._log
        self._d = [e] * (2 * self._size)
        self._lz = [self._id] * self._size
        for i in range(self._n):
            self._d[self._size + i] = v[i]
        for i in range(self._size - 1, 0, -1):
            self._update(i)

    def set(self, p: int, x: typing.Any) -> None:
        assert 0 <= p < self._n

        p += self._size
        for i in range(self._log, 0, -1):
            self._push(p >> i)
        self._d[p] = x
        for i in range(1, self._log + 1):
            self._update(p >> i)

    def get(self, p: int) -> typing.Any:
        assert 0 <= p < self._n

        p += self._size
        for i in range(self._log, 0, -1):
            self._push(p >> i)
        return self._d[p]

    def prod(self, left: int, right: int) -> typing.Any:
        assert 0 <= left <= right <= self._n

        if left == right:
            return self._e

        left += self._size
        right += self._size

        for i in range(self._log, 0, -1):
            if ((left >> i) << i) != left:
                self._push(left >> i)
            if ((right >> i) << i) != right:
                self._push((right - 1) >> i)

        sml = self._e
        smr = self._e
        while left < right:
            if left & 1:
                sml = self._op(sml, self._d[left])
                left += 1
            if right & 1:
                right -= 1
                smr = self._op(self._d[right], smr)
            left >>= 1
            right >>= 1

        return self._op(sml, smr)

    def all_prod(self) -> typing.Any:
        return self._d[1]

    def apply(self, left: int, right: typing.Optional[int] = None,
              f: typing.Optional[typing.Any] = None) -> None:
        assert f is not None

        if right is None:
            p = left
            assert 0 <= left < self._n

            p += self._size
            for i in range(self._log, 0, -1):
                self._push(p >> i)
            self._d[p] = self._mapping(f, self._d[p])
            for i in range(1, self._log + 1):
                self._update(p >> i)
        else:
            assert 0 <= left <= right <= self._n
            if left == right:
                return

            left += self._size
            right += self._size

            for i in range(self._log, 0, -1):
                if ((left >> i) << i) != left:
                    self._push(left >> i)
                if ((right >> i) << i) != right:
                    self._push((right - 1) >> i)

            l2 = left
            r2 = right
            while left < right:
                if left & 1:
                    self._all_apply(left, f)
                    left += 1
                if right & 1:
                    right -= 1
                    self._all_apply(right, f)
                left >>= 1
                right >>= 1
            left = l2
            right = r2

            for i in range(1, self._log + 1):
                if ((left >> i) << i) != left:
                    self._update(left >> i)
                if ((right >> i) << i) != right:
                    self._update((right - 1) >> i)

    def max_right(
            self, left: int, g: typing.Callable[[typing.Any], bool]) -> int:
        assert 0 <= left <= self._n
        assert g(self._e)

        if left == self._n:
            return self._n

        left += self._size
        for i in range(self._log, 0, -1):
            self._push(left >> i)

        sm = self._e
        first = True
        while first or (left & -left) != left:
            first = False
            while left % 2 == 0:
                left >>= 1
            if not g(self._op(sm, self._d[left])):
                while left < self._size:
                    self._push(left)
                    left *= 2
                    if g(self._op(sm, self._d[left])):
                        sm = self._op(sm, self._d[left])
                        left += 1
                return left - self._size
            sm = self._op(sm, self._d[left])
            left += 1

        return self._n

    def min_left(self, right: int, g: typing.Any) -> int:
        assert 0 <= right <= self._n
        assert g(self._e)

        if right == 0:
            return 0

        right += self._size
        for i in range(self._log, 0, -1):
            self._push((right - 1) >> i)

        sm = self._e
        first = True
        while first or (right & -right) != right:
            first = False
            right -= 1
            while right > 1 and right % 2:
                right >>= 1
            if not g(self._op(self._d[right], sm)):
                while right < self._size:
                    self._push(right)
                    right = 2 * right + 1
                    if g(self._op(self._d[right], sm)):
                        sm = self._op(self._d[right], sm)
                        right -= 1
                return right + 1 - self._size
            sm = self._op(self._d[right], sm)

        return 0

    def _update(self, k: int) -> None:
        self._d[k] = self._op(self._d[2 * k], self._d[2 * k + 1])

    def _all_apply(self, k: int, f: typing.Any) -> None:
        self._d[k] = self._mapping(f, self._d[k])
        if k < self._size:
            self._lz[k] = self._composition(f, self._lz[k])

    def _push(self, k: int) -> None:
        self._all_apply(2 * k, self._lz[k])
        self._all_apply(2 * k + 1, self._lz[k])
        self._lz[k] = self._id