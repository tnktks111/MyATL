"""
セグメント木（Segment Tree）。

モノイドに対する区間積を管理するデータ構造である。
配列の1点を更新しながら、任意の半開区間 [left, right) に
含まれる要素の総積を O(log N) で取得できる。

ここでいう「積」とは乗算に限らず、指定した二項演算 op による
集約結果を指す。たとえば、次のような演算を扱える。

    ・区間和
    ・区間最小値
    ・区間最大値
    ・区間GCD
    ・行列積
    ・文字列の連結

二項演算 op と単位元 e は、次の条件を満たす必要がある。

結合則:
    任意の a, b, c に対して、

        op(op(a, b), c) == op(a, op(b, c))

    が成り立つ。

単位元:
    任意の a に対して、

        op(e, a) == op(a, e) == a

    が成り立つ。

op が可換である必要はない。
区間内の要素は、元の配列における左から右への順序で演算される。

添字は 0 以上 N 未満とする。
区間は半開区間 [left, right) で指定する。
すなわち、left は含み、right は含まない。

初期化:
    SegTree(op, e, v)

    op:
        区間を集約する二項演算。

    e:
        op の単位元。

    v:
        初期配列、または配列の長さ。

        リストを渡した場合、その内容で初期化する。
        整数 N を渡した場合、長さ N の配列を作成し、
        すべての要素を単位元 e で初期化する。

計算量:
    構築:
        O(N)

    1点更新:
        O(log N)

    1点取得:
        O(1)

    区間積:
        O(log N)

    max_right():
        O(log N)

    min_left():
        O(log N)

    全区間の積:
        O(1)

空間計算量:
    O(N)

主なメソッド:
    set(p, x):
        配列の p 番目の要素を x に変更する。

    get(p):
        配列の p 番目の要素を返す。

    prod(left, right):
        半開区間 [left, right) の総積を返す。

        空区間の場合、すなわち left == right の場合は、
        単位元 e を返す。

    all_prod():
        配列全体、すなわち区間 [0, N) の総積を返す。

    max_right(left, f):
        left を固定し、条件

            f(prod(left, right)) == True

        を満たす最大の right を返す。

        戻り値 right は、次の条件を満たす。

            f(prod(left, right)) == True

        さらに right < N の場合は、

            f(prod(left, right + 1)) == False

        が成り立つ。

    min_left(right, f):
        right を固定し、条件

            f(prod(left, right)) == True

        を満たす最小の left を返す。

        戻り値 left は、次の条件を満たす。

            f(prod(left, right)) == True

        さらに left > 0 の場合は、

            f(prod(left - 1, right)) == False

        が成り立つ。

max_right() と min_left() の条件:
    判定関数 f は、単位元に対して True を返す必要がある。

        f(e) == True

    また、正しい境界を二分探索するためには、探索する区間において
    判定結果が単調に変化する必要がある。

    典型例として、要素がすべて非負の区間和について、

        f(x) = (x <= limit)

    とすれば、区間和が limit 以下である最大区間を探索できる。

    f は同じ引数に対して常に同じ結果を返し、
    呼び出しによって内部状態を変化させてはならない。

使用例（区間和）:
    values = [2, 1, 3, 2, 4]

    segtree = SegTree(
        op=lambda a, b: a + b,
        e=0,
        v=values,
    )

    区間 [1, 4) の和を取得する場合:

        print(segtree.prod(1, 4))

    出力:

        6

    2番目の要素を10に変更する場合:

        segtree.set(2, 10)
        print(segtree.get(2))
        print(segtree.all_prod())

    出力:

        10
        19

使用例（max_right）:
    values = [2, 1, 3, 2, 4]

    segtree = SegTree(
        op=lambda a, b: a + b,
        e=0,
        v=values,
    )

    位置0から始めて、区間和が6以下となる最大の right を
    求める場合:

        right = segtree.max_right(
            0,
            lambda value: value <= 6,
        )
        print(right)

    出力:

        3

    このとき、

        sum(values[0:3]) == 6
        sum(values[0:4]) == 8

    である。

使用例（min_left）:
    位置5を右端として、区間和が6以下となる最小の left を
    求める場合:

        left = segtree.min_left(
            5,
            lambda value: value <= 6,
        )
        print(left)

    出力:

        3

    このとき、

        sum(values[3:5]) == 6
        sum(values[2:5]) == 9

    である。

使用例（区間最小値）:
    INF = float("inf")
    values = [5, 3, 7, 1, 4]

    segtree = SegTree(
        op=min,
        e=INF,
        v=values,
    )

    print(segtree.prod(1, 4))

    出力:

        1

注意:
    set() は1点更新であり、区間全体を一度に更新する機能はない。
    区間更新も O(log N) で行いたい場合は、遅延評価セグメント木
    （Lazy Segment Tree）を使用する必要がある。

Reference:
    AtCoder Library,
    "segtree",
    https://atcoder.github.io/ac-library/production/document_ja/segtree.html
"""



import typing

def _ceil_pow2(n: int) -> int:
    x = 0
    while (1 << x) < n:
        x += 1

    return x

class SegTree:
    def __init__(self,
                 op: typing.Callable[[typing.Any, typing.Any], typing.Any],
                 e: typing.Any,
                 v: typing.Union[int, typing.List[typing.Any]]) -> None:
        self._op = op
        self._e = e

        if isinstance(v, int):
            v = [e] * v

        self._n = len(v)
        self._log = _ceil_pow2(self._n)
        self._size = 1 << self._log
        self._d = [e] * (2 * self._size)

        for i in range(self._n):
            self._d[self._size + i] = v[i]
        for i in range(self._size - 1, 0, -1):
            self._update(i)

    def set(self, p: int, x: typing.Any) -> None:
        assert 0 <= p < self._n

        p += self._size
        self._d[p] = x
        for i in range(1, self._log + 1):
            self._update(p >> i)

    def get(self, p: int) -> typing.Any:
        assert 0 <= p < self._n

        return self._d[p + self._size]

    def prod(self, left: int, right: int) -> typing.Any:
        assert 0 <= left <= right <= self._n
        sml = self._e
        smr = self._e
        left += self._size
        right += self._size

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

    def max_right(self, left: int,
                  f: typing.Callable[[typing.Any], bool]) -> int:
        assert 0 <= left <= self._n
        assert f(self._e)

        if left == self._n:
            return self._n

        left += self._size
        sm = self._e

        first = True
        while first or (left & -left) != left:
            first = False
            while left % 2 == 0:
                left >>= 1
            if not f(self._op(sm, self._d[left])):
                while left < self._size:
                    left *= 2
                    if f(self._op(sm, self._d[left])):
                        sm = self._op(sm, self._d[left])
                        left += 1
                return left - self._size
            sm = self._op(sm, self._d[left])
            left += 1

        return self._n

    def min_left(self, right: int,
                 f: typing.Callable[[typing.Any], bool]) -> int:
        assert 0 <= right <= self._n
        assert f(self._e)

        if right == 0:
            return 0

        right += self._size
        sm = self._e

        first = True
        while first or (right & -right) != right:
            first = False
            right -= 1
            while right > 1 and right % 2:
                right >>= 1
            if not f(self._op(self._d[right], sm)):
                while right < self._size:
                    right = 2 * right + 1
                    if f(self._op(self._d[right], sm)):
                        sm = self._op(self._d[right], sm)
                        right -= 1
                return right + 1 - self._size
            sm = self._op(self._d[right], sm)

        return 0

    def _update(self, k: int) -> None:
        self._d[k] = self._op(self._d[2 * k], self._d[2 * k + 1])