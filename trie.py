"""文字列集合を管理する Trie。"""


class _TrieNode:
    __slots__ = ("children", "is_terminal")

    def __init__(self) -> None:
        self.children: dict[str, _TrieNode] = {}
        self.is_terminal = False


class Trie:
    """重複を持たない文字列集合の Trie。

    空文字も登録できる。``insert`` の重複は状態を変えず、存在しない文字列の
    ``delete`` は ``False``。長さ :math:`L` の文字列に対する各操作は通常
    :math:`O(L)`、空間は作成されたノード数に比例する。子の辞書と根は公開
    しないため、列挙には ``words`` を使う。
    """

    def __init__(self) -> None:
        self._root = _TrieNode()
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, word: str) -> bool:
        """``word`` を追加し、新規登録なら ``True`` を返す。"""
        node = self._root
        for char in word:
            next_node = node.children.get(char)
            if next_node is None:
                next_node = _TrieNode()
                node.children[char] = next_node
            node = next_node
        if node.is_terminal:
            return False
        node.is_terminal = True
        self._size += 1
        return True

    def search(self, word: str) -> bool:
        """``word`` が登録済みなら ``True`` を返す。"""
        node = self._root
        for char in word:
            next_node = node.children.get(char)
            if next_node is None:
                return False
            node = next_node
        return node.is_terminal

    def delete(self, word: str) -> bool:
        """``word`` を論理削除し、存在していた場合だけ ``True`` を返す。"""
        node = self._root
        for char in word:
            next_node = node.children.get(char)
            if next_node is None:
                return False
            node = next_node
        if not node.is_terminal:
            return False
        node.is_terminal = False
        self._size -= 1
        return True

    def words(self) -> list[str]:
        """登録文字列を辞書順で返す。計算量は出力文字数以上。"""
        result: list[str] = []
        stack = [(self._root, "")]
        while stack:
            node, prefix = stack.pop()
            if node.is_terminal:
                result.append(prefix)
            for char in sorted(node.children, reverse=True):
                stack.append((node.children[char], prefix + char))
        return result

__all__ = ["Trie"]
