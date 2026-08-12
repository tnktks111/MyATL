"""Fenwick TreeとSegment Tree 2種の差分テスト。"""

import random

from fenwick import FenwickTree
from lazy_seg_tree import LazySegTree
from seg_tree import SegTree


def test_fenwick_empty_and_search_boundaries() -> None:
    empty = FenwickTree(0)
    assert empty.sum(0, 0) == 0
    assert empty.lower_bound(1) == 0
    assert empty.upper_bound(0) == 0
    tree = FenwickTree(5)
    for index, value in enumerate([0, 2, 0, 3, 0]):
        tree.add(index, value)
    assert [tree.lower_bound(x) for x in [0, 1, 2, 3, 5, 6]] == [0, 1, 1, 3, 3, 5]
    assert [tree.upper_bound(x) for x in [-1, 0, 1, 2, 4, 5]] == [0, 1, 1, 3, 3, 5]


def test_fenwick_matches_list_for_updates_ranges_and_bounds() -> None:
    rng = random.Random(12345)
    for n in range(16):
        values = [0] * n
        tree = FenwickTree(n)
        for _ in range(100):
            if n and rng.randrange(2) == 0:
                index = rng.randrange(n)
                value = rng.randrange(6)
                values[index] += value
                tree.add(index, value)
            left = rng.randrange(n + 1)
            right = rng.randrange(left, n + 1)
            assert tree.sum(left, right) == sum(values[left:right])
            for target in range(-1, sum(values) + 2):
                lower = (0 if target <= 0 else next(
                    (i for i in range(n) if sum(values[:i + 1]) >= target), n
                ))
                upper = (0 if target < 0 else next(
                    (i for i in range(n) if sum(values[:i + 1]) > target), n
                ))
                assert tree.lower_bound(target) == lower
                assert tree.upper_bound(target) == upper


def test_segment_tree_preserves_non_commutative_order() -> None:
    tree = SegTree(lambda left, right: left + right, "", list("abcdef"))
    assert tree.prod(1, 5) == "bcde"
    tree.set(2, "X")
    assert tree.all_prod() == "abXdef"


def test_segment_tree_random_ranges_and_boundary_searches() -> None:
    rng = random.Random(98765)
    for n in range(18):
        values = [rng.randrange(6) for _ in range(n)]
        tree = SegTree(lambda left, right: left + right, 0, values)
        assert tree.prod(0, 0) == 0
        for _ in range(100):
            if n and rng.randrange(3) == 0:
                index = rng.randrange(n)
                values[index] = rng.randrange(6)
                tree.set(index, values[index])
            left = rng.randrange(n + 1)
            right = rng.randrange(left, n + 1)
            assert tree.prod(left, right) == sum(values[left:right])
            limit = rng.randrange(20)
            expected_right = left
            while (expected_right < n
                   and sum(values[left:expected_right + 1]) <= limit):
                expected_right += 1
            assert tree.max_right(left, lambda total: total <= limit) == expected_right
            expected_left = right
            while (expected_left > 0
                   and sum(values[expected_left - 1:right]) <= limit):
                expected_left -= 1
            assert tree.min_left(right, lambda total: total <= limit) == expected_left


def _make_affine_sum_tree(values: list[int]) -> LazySegTree:
    def op(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
        return left[0] + right[0], left[1] + right[1]

    def mapping(action: tuple[int, int], value: tuple[int, int]) -> tuple[int, int]:
        multiplier, addition = action
        total, length = value
        return multiplier * total + addition * length, length

    def composition(new: tuple[int, int], old: tuple[int, int]) -> tuple[int, int]:
        return new[0] * old[0], new[0] * old[1] + new[1]

    return LazySegTree(
        op, (0, 0), mapping, composition, (1, 0),
        [(value, 1) for value in values],
    )


def test_lazy_segment_tree_composition_order_and_point_call_forms() -> None:
    tree = _make_affine_sum_tree([1, 2, 3])
    tree.apply(0, 3, (2, 1))
    tree.apply(0, 3, (3, 4))
    assert [tree.get(i)[0] for i in range(3)] == [13, 19, 25]
    tree.apply(1, (0, 7))
    tree.apply(2, f=(1, 5))
    assert [tree.get(i)[0] for i in range(3)] == [13, 7, 30]


def test_lazy_segment_tree_matches_naive_affine_updates_and_searches() -> None:
    rng = random.Random(424242)
    for n in range(15):
        values = [rng.randrange(5) for _ in range(n)]
        tree = _make_affine_sum_tree(values)
        for _ in range(120):
            operation = rng.randrange(4)
            if operation == 0 and n:
                index = rng.randrange(n)
                action = rng.randrange(2), rng.randrange(4)
                tree.apply(index, action)
                values[index] = action[0] * values[index] + action[1]
            elif operation == 1:
                left = rng.randrange(n + 1)
                right = rng.randrange(left, n + 1)
                action = rng.randrange(2), rng.randrange(4)
                tree.apply(left, right, action)
                for index in range(left, right):
                    values[index] = action[0] * values[index] + action[1]
            left = rng.randrange(n + 1)
            right = rng.randrange(left, n + 1)
            assert tree.prod(left, right) == (sum(values[left:right]), right - left)
            limit = rng.randrange(30)
            expected_right = left
            while (expected_right < n
                   and sum(values[left:expected_right + 1]) <= limit):
                expected_right += 1
            assert tree.max_right(left, lambda value: value[0] <= limit) == expected_right
            expected_left = right
            while (expected_left > 0
                   and sum(values[expected_left - 1:right]) <= limit):
                expected_left -= 1
            assert tree.min_left(right, lambda value: value[0] <= limit) == expected_left


def test_segment_trees_support_zero_length() -> None:
    segment = SegTree(lambda left, right: left + right, 0, 0)
    assert segment.all_prod() == segment.prod(0, 0) == 0
    assert segment.max_right(0, lambda value: value == 0) == 0
    assert segment.min_left(0, lambda value: value == 0) == 0
    lazy = _make_affine_sum_tree([])
    lazy.apply(0, 0, (2, 3))
    assert lazy.all_prod() == lazy.prod(0, 0) == (0, 0)
