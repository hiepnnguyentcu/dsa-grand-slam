"""Fenwick tree (Binary Indexed Tree) — prefix sums that survive point updates.

Signs: range sum queries AND element updates interleaved, "count of smaller
       numbers after self", inversions, rank of a value in a growing stream,
       range add + point query online.
Approach: tree[i] (1-based) stores the sum of the last lowbit(i) elements
          ending at i, where lowbit(i) = i & -i. A prefix query strips the
          low bit (i -= i & -i), an update adds it (i += i & -i); either way
          about log n steps. Range sum = prefix(r + 1) - prefix(l), exactly
          like a static prefix array.
          Counting problems: index the tree by VALUE (after coordinate
          compression) and store counts; prefix(v) = how many seen are < v.
Complexity: O(log n) per update and per prefix query, O(n) build, O(n) space.
Gotchas:
  - The tree is 1-based internally; index 0 would loop forever (0 & -0 == 0).
  - "Set a[i] = v" is add(i, v - a[i]): keep a copy of the array.
  - Compress values to 0..m-1 before counting; negatives and 1e9 break a
    value-indexed array otherwise.
  - Range add + point query: put a Fenwick on the difference array.
    Range add + range sum needs two trees (or a segment tree with lazy).
  - min / max with arbitrary updates: use a segment tree.

Run the tests at the bottom with:  python3 prefix_sums/fenwick.py
"""

import random
from bisect import bisect_left


# ---------------------------------------------------------------- implementation


class Fenwick:
    """Point add, prefix sum, range sum over indices 0..n-1."""

    def __init__(self, n_or_values):
        if isinstance(n_or_values, int):
            self.n = n_or_values
            self.tree = [0] * (self.n + 1)
        else:                                   # O(n) build: push each node to its parent
            self.n = len(n_or_values)
            self.tree = [0] + list(n_or_values)
            for i in range(1, self.n + 1):
                j = i + (i & -i)
                if j <= self.n:
                    self.tree[j] += self.tree[i]

    def add(self, i, delta):
        """a[i] += delta."""
        i += 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & -i

    def prefix(self, i):
        """sum(a[:i])."""
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & -i
        return s

    def range_sum(self, l, r):
        """sum(a[l..r]), inclusive."""
        return self.prefix(r + 1) - self.prefix(l)


class NumArrayMutable:
    """Range Sum Query - Mutable: update(i, val) and sum_range(l, r)."""

    def __init__(self, nums):
        self.a = list(nums)
        self.bit = Fenwick(nums)

    def update(self, i, val):
        self.bit.add(i, val - self.a[i])
        self.a[i] = val

    def sum_range(self, l, r):
        return self.bit.range_sum(l, r)


class RangeAddFenwick:
    """Range add, point query: a Fenwick over the difference array."""

    def __init__(self, n):
        self.bit = Fenwick(n + 1)

    def range_add(self, l, r, v):
        self.bit.add(l, v)
        self.bit.add(r + 1, -v)

    def get(self, i):
        return self.bit.prefix(i + 1)


def count_smaller(nums):
    """out[i] = how many j > i have nums[j] < nums[i].

    Walk right to left; the tree counts values seen so far, indexed by rank.
    """
    ranks = sorted(set(nums))
    bit = Fenwick(len(ranks))
    out = [0] * len(nums)
    for i in range(len(nums) - 1, -1, -1):
        r = bisect_left(ranks, nums[i])
        out[i] = bit.prefix(r)            # strictly smaller ranks
        bit.add(r, 1)
    return out


def count_inversions(nums):
    """Pairs i < j with nums[i] > nums[j]."""
    return sum(count_smaller(nums))


# ------------------------------------------------------------------------ tests


def test_fenwick_build_matches_repeated_add():
    random.seed(61)
    for _ in range(100):
        a = [random.randint(-9, 9) for _ in range(random.randint(0, 20))]
        built, added = Fenwick(a), Fenwick(len(a))
        for i, x in enumerate(a):
            added.add(i, x)
        assert built.tree == added.tree


def test_num_array_mutable_example():
    na = NumArrayMutable([1, 3, 5])
    assert na.sum_range(0, 2) == 9
    na.update(1, 2)
    assert na.sum_range(0, 2) == 8


def test_mutable_matches_plain_list_under_random_ops():
    random.seed(62)
    for _ in range(50):
        a = [random.randint(-9, 9) for _ in range(random.randint(1, 20))]
        na = NumArrayMutable(a)
        for _ in range(100):
            if random.random() < 0.5:
                i, v = random.randrange(len(a)), random.randint(-9, 9)
                a[i] = v
                na.update(i, v)
            else:
                l = random.randrange(len(a))
                r = random.randrange(l, len(a))
                assert na.sum_range(l, r) == sum(a[l:r + 1])


def test_range_add_point_query_matches_brute_force():
    random.seed(63)
    for _ in range(50):
        n = random.randint(1, 15)
        f, a = RangeAddFenwick(n), [0] * n
        for _ in range(60):
            l = random.randrange(n)
            r = random.randrange(l, n)
            v = random.randint(-5, 5)
            f.range_add(l, r, v)
            for i in range(l, r + 1):
                a[i] += v
            i = random.randrange(n)
            assert f.get(i) == a[i]


def test_count_smaller_examples():
    assert count_smaller([5, 2, 6, 1]) == [2, 1, 1, 0]
    assert count_smaller([-1, -1]) == [0, 0]       # equal is not smaller
    assert count_smaller([]) == []


def test_count_smaller_matches_brute_force():
    random.seed(64)
    for _ in range(300):
        a = [random.randint(-10**9, 10**9) if random.random() < 0.3 else random.randint(-5, 5)
             for _ in range(random.randint(0, 15))]
        want = [sum(a[j] < a[i] for j in range(i + 1, len(a))) for i in range(len(a))]
        assert count_smaller(a) == want


def test_count_inversions():
    assert count_inversions([1, 2, 3]) == 0
    assert count_inversions([3, 2, 1]) == 3
    assert count_inversions([2, 4, 1, 3, 5]) == 3


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
