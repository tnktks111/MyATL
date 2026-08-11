"""
文字列のローリングハッシュ。

プログラム起動時にランダムな基数 BASE を1度だけ生成する。
すべてのインスタンスで同じ BASE と MOD を使用するため、
異なる文字列の部分文字列同士も比較できる。

ハッシュ衝突が発生する可能性はあるが、
ランダムな基数と 2^61 - 1 を法として使用することで、
衝突確率を非常に小さくしている。

添字は0以上N未満とする。
区間は半開区間 [left, right) で指定する。

計算量:
    構築:
        O(N)

    部分文字列のハッシュ値の取得:
        O(1)

空間計算量:
    O(N)

主なメソッド:
    get(left, right):
        部分文字列 s[left:right] のハッシュ値を返す。

使用例:
    s = "abracadabra"
    rolling_hash = RollingHash(s)

    print(
        rolling_hash.get(0, 4)
        == rolling_hash.get(7, 11)
    )

出力:
    True

異なる文字列の部分文字列を比較する場合:
    rh_s = RollingHash("abracadabra")
    rh_t = RollingHash("abra")

    same = (
        rh_s.get(0, 4)
        == rh_t.get(0, 4)
    )
"""

from random import SystemRandom

class RollingHash:
    MOD = (1 << 61) - 1
    BASE = SystemRandom().randrange(2, MOD - 1)

    def __init__(self, s: str) -> None:
        self._n = len(s)
        self._hash = [0] * (self._n + 1)
        self._power = [1] * (self._n + 1)

        for i, char in enumerate(s):
            self._hash[i + 1] = (
                self._hash[i] * self.BASE + ord(char)
            ) % self.MOD

            self._power[i + 1] = (
                self._power[i] * self.BASE
            ) % self.MOD

    def get(self, left: int, right: int) -> int:
        """
        部分文字列 s[left:right] のハッシュ値を返す。

        計算量:
            O(1)
        """
        assert 0 <= left <= right <= self._n

        return (
            self._hash[right]
            - self._hash[left] * self._power[right - left]
        ) % self.MOD
