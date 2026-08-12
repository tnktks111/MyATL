"""文字列の部分文字列を比較する Rolling Hash。"""

from random import SystemRandom


class RollingHash:
    """法 ``2**61 - 1`` の多項式ハッシュを構築する。

    同一プロセスの全インスタンスが同じ ``BASE`` と ``MOD`` を使うため、
    異なる文字列間でも比較できる。区間は0-indexedの半開区間
    ``[left, right)``。構築は :math:`O(N)`、``get`` と ``same`` は
    :math:`O(1)`、空間は :math:`O(N)`。

    Notes:
        確率的アルゴリズムであり、異なる文字列の衝突可能性はゼロではない。
        ``same`` は長さも確認する。厳密比較が必要なら元文字列を比較すること。
    """

    MOD = (1 << 61) - 1
    BASE = SystemRandom().randrange(256, MOD - 1)

    def __init__(self, text: str) -> None:
        self._n = len(text)
        self._hash = [0] * (self._n + 1)
        self._power = [1] * (self._n + 1)
        for index, char in enumerate(text):
            # +1 により先頭の NUL 文字を無視する決定的衝突を避ける。
            value = ord(char) + 1
            self._hash[index + 1] = (
                self._hash[index] * self.BASE + value
            ) % self.MOD
            self._power[index + 1] = (
                self._power[index] * self.BASE
            ) % self.MOD

    def __len__(self) -> int:
        return self._n

    def get(self, left: int, right: int) -> int:
        """部分文字列 ``text[left:right]`` のハッシュ値を返す。"""
        if not 0 <= left <= right <= self._n:
            raise IndexError("invalid half-open interval")
        return (
            self._hash[right]
            - self._hash[left] * self._power[right - left]
        ) % self.MOD

    def same(
        self,
        left: int,
        right: int,
        other: "RollingHash",
        other_left: int,
        other_right: int,
    ) -> bool:
        """2つの半開区間が同じ文字列と推定されるなら ``True`` を返す。"""
        hash_value = self.get(left, right)
        other_hash_value = other.get(other_left, other_right)
        length = right - left
        if length != other_right - other_left:
            return False
        return hash_value == other_hash_value


__all__ = ["RollingHash"]
