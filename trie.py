class TrieNode:
    def __init__(self):
        # 辞書型の定義、キー: 文字, 値: 子ノード(TrieNode)
        self.children = {}
        # そのノードが単語の終わりかどうかを表すフラグ
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()


    def insert(self, word: str) -> None:
        """文字列を追加する"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word: str) -> bool:
        """完全一致検索"""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word
    
    def delete(self, word: str) -> bool:
        """文字列を削除する（フラグを落とすだけの論理削除）"""
        node = self.root
        for char in word:
            if char not in node.children:
                return False  # 単語が存在しない
            node = node.children[char]
        
        if not node.is_end_of_word:
            return False  # そもそも登録されていない
            
        node.is_end_of_word = False
        return True


    def get_all_words_sorted(self) -> list[str]:
        """辞書順に全単語を取得する"""
        results = []
        
        def _dfs(node: TrieNode, prefix: str):
            if node.is_end_of_word:
                results.append(prefix)
            
            # 辞書順にするためにキーをソートして走査
            for char in sorted(node.children.keys()):
                _dfs(node.children[char], prefix + char)
                
        _dfs(self.root, "")
        return results