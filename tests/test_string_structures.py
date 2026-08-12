"""TrieとRolling Hashの集合・実文字列との差分テスト。"""

import random

from rolling_hash import RollingHash
from trie import Trie


def test_trie_duplicate_insert_missing_delete_empty_word_and_order() -> None:
    trie = Trie()
    assert trie.insert("")
    assert not trie.insert("")
    assert trie.insert("app")
    assert trie.insert("apple")
    assert not trie.delete("ap")
    assert not trie.delete("missing")
    assert trie.words() == ["", "app", "apple"]
    assert trie.delete("app")
    assert not trie.search("app")
    assert trie.search("apple")
    assert len(trie) == 2


def test_trie_matches_python_set_under_random_operations() -> None:
    rng = random.Random(112358)
    trie = Trie()
    expected: set[str] = set()
    candidates = [
        "".join(rng.choice("abc") for _ in range(rng.randrange(7)))
        for _ in range(100)
    ]
    for _ in range(500):
        word = rng.choice(candidates)
        operation = rng.randrange(3)
        if operation == 0:
            changed = word not in expected
            assert trie.insert(word) == changed
            expected.add(word)
        elif operation == 1:
            changed = word in expected
            assert trie.delete(word) == changed
            expected.discard(word)
        else:
            assert trie.search(word) == (word in expected)
        assert trie.words() == sorted(expected)
        assert len(trie) == len(expected)


def test_trie_word_listing_does_not_recurse() -> None:
    trie = Trie()
    word = "a" * 3000
    trie.insert(word)
    assert trie.words() == [word]


def test_rolling_hash_cross_instance_length_and_nul_handling() -> None:
    left = RollingHash("\0abracadabra")
    right = RollingHash("abra")
    assert left.same(1, 5, right, 0, 4)
    assert not left.same(0, 2, right, 3, 4)
    # 旧実装では先頭NULを数値0としていたため、以下が決定的に一致した。
    assert RollingHash("\0a").get(0, 2) != RollingHash("a").get(0, 1)
    assert RollingHash("").get(0, 0) == 0


def test_rolling_hash_matches_actual_substring_equality() -> None:
    rng = random.Random(161803)
    texts = [
        "".join(rng.choice("abc\0") for _ in range(rng.randrange(15)))
        for _ in range(20)
    ]
    hashes = [RollingHash(text) for text in texts]
    for _ in range(1000):
        first_index = rng.randrange(len(texts))
        second_index = rng.randrange(len(texts))
        first_left = rng.randrange(len(texts[first_index]) + 1)
        first_right = rng.randrange(first_left, len(texts[first_index]) + 1)
        second_left = rng.randrange(len(texts[second_index]) + 1)
        second_right = rng.randrange(second_left, len(texts[second_index]) + 1)
        actual = (
            texts[first_index][first_left:first_right]
            == texts[second_index][second_left:second_right]
        )
        assert hashes[first_index].same(
            first_left,
            first_right,
            hashes[second_index],
            second_left,
            second_right,
        ) == actual

