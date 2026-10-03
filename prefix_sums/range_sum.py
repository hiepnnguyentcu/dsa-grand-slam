"""1D prefix sums — O(1) range sums, pivot index, split points.

Signs: many "sum of a[l..r]" queries on an array that never changes, "left
       sum equals right sum", "number of ways to split", averages over a
       window of every position.
Approach: p[i] = a[0] + ... + a[i-1], with p[0] = 0. Then
          sum(a[l..r]) = p[r + 1] - p[l]. One O(n) pass buys O(1) queries.
          Split problems compare p[i] (left part) with total - p[i] (right).
Complexity: O(n) build, O(1) per query, O(n) space (O(1) if you only need a
            running sum and the total).
Gotchas:
  - Size n + 1 with p[0] = 0. It removes every "if l == 0" special case.
  - Inclusive r maps to p[r + 1]. Off-by-one here is the classic bug.
  - Python ints never overflow; in Java/C++ use long for p.
  - The array changes between queries -> Fenwick tree (fenwick.py).
  - Many range *updates*, then reads -> difference array (difference_array.py).

Run the tests at the bottom with:  python3 prefix_sums/range_sum.py
"""

import random


# ---------------------------------------------------------------- implementation


def build(a):
    """p[i] = sum(a[:i]); len(p) == len(a) + 1."""
    p = [0] * (len(a) + 1)
    for i, x in enumerate(a):
        p[i + 1] = p[i] + x
    return p


def range_sum(p, l, r):
    """sum(a[l..r]), both ends inclusive."""
    return p[r + 1] - p[l]


class NumArray:
    """Range Sum Query - Immutable: build once, answer sum_range in O(1)."""

    def __init__(self, nums):
        self.p = build(nums)

    def sum_range(self, left, right):
        return self.p[right + 1] - self.p[left]


def pivot_index(a):
    """Leftmost i with sum(a[:i]) == sum(a[i+1:]), or -1.

    No array needed: keep the left sum; the right sum is total - left - a[i].
    """
    total, left = sum(a), 0
    for i, x in enumerate(a):
        if left == total - left - x:
            return i
        left += x
    return -1


def ways_to_split(a):
    """Count i in [0, n-2] with sum(a[:i+1]) >= sum(a[i+1:]).

    Both parts must be non-empty, so the last index is not a split.
    """
    total, left, count = sum(a), 0, 0
    for x in a[:-1]:
        left += x
        if left >= total - left:
            count += 1
    return count


def k_radius_averages(a, k):
    """avg[i] = floor mean of a[i-k..i+k], or -1 if the window leaves the array."""
    n, p = len(a), build(a)
    out = [-1] * n
    for i in range(k, n - k):
        out[i] = (p[i + k + 1] - p[i - k]) // (2 * k + 1)
    return out


# ------------------------------------------------------------------------ tests


def test_build_and_query_example():
    p = build([3, -1, 4, 1, 5])
    assert p == [0, 3, 2, 6, 7, 12]
    assert range_sum(p, 0, 4) == 12
    assert range_sum(p, 1, 3) == 4
    assert range_sum(p, 2, 2) == 4


def test_range_sum_matches_brute_force():
    random.seed(1)
    for _ in range(200):
        a = [random.randint(-20, 20) for _ in range(random.randint(1, 15))]
        na = NumArray(a)
        for _ in range(10):
            l = random.randrange(len(a))
            r = random.randrange(l, len(a))
            assert na.sum_range(l, r) == sum(a[l:r + 1])


def test_empty_array_builds():
    assert build([]) == [0]


def test_pivot_index_examples():
    assert pivot_index([1, 7, 3, 6, 5, 6]) == 3
    assert pivot_index([1, 2, 3]) == -1
    assert pivot_index([2, 1, -1]) == 0  # empty left side sums to 0
    assert pivot_index([0]) == 0


def test_pivot_index_matches_brute_force():
    random.seed(2)
    for _ in range(300):
        a = [random.randint(-3, 3) for _ in range(random.randint(1, 10))]
        want = next((i for i in range(len(a)) if sum(a[:i]) == sum(a[i + 1:])), -1)
        assert pivot_index(a) == want


def test_ways_to_split_matches_brute_force():
    random.seed(3)
    assert ways_to_split([10, 4, -8, 7]) == 2
    for _ in range(300):
        a = [random.randint(-10, 10) for _ in range(random.randint(2, 10))]
        want = sum(sum(a[:i + 1]) >= sum(a[i + 1:]) for i in range(len(a) - 1))
        assert ways_to_split(a) == want


def test_k_radius_averages_matches_brute_force():
    random.seed(4)
    assert k_radius_averages([7, 4, 3, 9, 1, 8, 5, 2, 6], 3) == [-1, -1, -1, 5, 4, 4, -1, -1, -1]
    for _ in range(200):
        a = [random.randint(0, 50) for _ in range(random.randint(1, 12))]
        k = random.randint(0, 4)
        want = [sum(a[i - k:i + k + 1]) // (2 * k + 1) if k <= i < len(a) - k else -1
                for i in range(len(a))]
        assert k_radius_averages(a, k) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
