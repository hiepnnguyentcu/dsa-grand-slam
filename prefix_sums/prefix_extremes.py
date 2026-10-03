"""Prefix min/max and suffix arrays — best split point, best pair, water.

Signs: "best i < j" pairs (buy low, sell high), "every element left of the
       cut <= every element right", "two non-overlapping windows", water
       trapped between the tallest walls on each side.
Approach: for each position, precompute the best thing strictly on its left
          (prefix max/min/best-window) and on its right (suffix). Then one
          scan tries every split or every j in O(1) each. Often the prefix
          side collapses to a running variable.
Complexity: O(n) time, O(n) space for suffix arrays (O(1) when a running
            variable suffices, or with two pointers for trapping water).
Gotchas:
  - Decide whether the split index belongs to the left or the right side,
    and keep both parts non-empty.
  - Update the running best AFTER using it for pairs i < j, so i != j.
  - Two windows: try both orders (L before M, and M before L).
  - Prefix min/max cannot answer arbitrary [l..r] (no inverse): only [0..r]
    or [l..n-1]. Arbitrary ranges need a sparse table or segment tree.

Run the tests at the bottom with:  python3 prefix_sums/prefix_extremes.py
"""

import random


# ---------------------------------------------------------------- implementation


def max_profit(prices):
    """Best Time to Buy and Sell Stock: max p[j] - p[i], i < j, or 0."""
    best, low = 0, float("inf")
    for p in prices:
        best = max(best, p - low)       # sell today against the cheapest past day
        low = min(low, p)
    return best


def best_sightseeing_pair(values):
    """max values[i] + values[j] + i - j over i < j.

    Split into (values[i] + i) + (values[j] - j); keep a running max of the
    first part over everything left of j.
    """
    best, left = float("-inf"), values[0] + 0
    for j in range(1, len(values)):
        best = max(best, left + values[j] - j)
        left = max(left, values[j] + j)
    return best


def trap(height):
    """Trapping Rain Water: water at i = min(max left, max right) - height[i]."""
    n = len(height)
    if n == 0:
        return 0
    left, right = [0] * n, [0] * n
    left[0], right[-1] = height[0], height[-1]
    for i in range(1, n):
        left[i] = max(left[i - 1], height[i])
    for i in range(n - 2, -1, -1):
        right[i] = max(right[i + 1], height[i])
    return sum(min(left[i], right[i]) - height[i] for i in range(n))


def partition_disjoint(a):
    """Smallest left length so max(left) <= min(right); both parts non-empty."""
    n = len(a)
    suffix_min = [0] * n
    suffix_min[-1] = a[-1]
    for i in range(n - 2, -1, -1):
        suffix_min[i] = min(suffix_min[i + 1], a[i])
    left_max = float("-inf")
    for i in range(n - 1):
        left_max = max(left_max, a[i])
        if left_max <= suffix_min[i + 1]:
            return i + 1
    return -1  # unreachable when an answer is guaranteed


def max_sum_two_no_overlap(a, L, M):
    """Max sum of two non-overlapping windows of lengths L and M.

    Prefix sums give each window's sum in O(1). Walking the right window's
    end, keep the best left window that ends before it. Try both orders.
    """
    p = [0]
    for x in a:
        p.append(p[-1] + x)

    def best(first, second):
        out = best_first = float("-inf")
        for end in range(first + second, len(a) + 1):     # end of the second window
            best_first = max(best_first, p[end - second] - p[end - second - first])
            out = max(out, best_first + p[end] - p[end - second])
        return out

    return max(best(L, M), best(M, L))


# ------------------------------------------------------------------------ tests


def test_max_profit_matches_brute_force():
    random.seed(51)
    assert max_profit([7, 1, 5, 3, 6, 4]) == 5
    assert max_profit([7, 6, 4, 3, 1]) == 0
    for _ in range(300):
        p = [random.randint(0, 20) for _ in range(random.randint(1, 12))]
        want = max([0] + [p[j] - p[i] for i in range(len(p)) for j in range(i + 1, len(p))])
        assert max_profit(p) == want


def test_best_sightseeing_pair_matches_brute_force():
    random.seed(52)
    assert best_sightseeing_pair([8, 1, 5, 2, 6]) == 11
    assert best_sightseeing_pair([1, 2]) == 2
    for _ in range(300):
        v = [random.randint(1, 20) for _ in range(random.randint(2, 12))]
        want = max(v[i] + v[j] + i - j for i in range(len(v)) for j in range(i + 1, len(v)))
        assert best_sightseeing_pair(v) == want


def test_trap_matches_brute_force():
    random.seed(53)
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert trap([4, 2, 0, 3, 2, 5]) == 9
    assert trap([]) == 0
    for _ in range(300):
        h = [random.randint(0, 8) for _ in range(random.randint(1, 12))]
        want = sum(max(0, min(max(h[:i + 1]), max(h[i:])) - h[i]) for i in range(len(h)))
        assert trap(h) == want


def test_partition_disjoint_matches_brute_force():
    random.seed(54)
    assert partition_disjoint([5, 0, 3, 8, 6]) == 3
    assert partition_disjoint([1, 1, 1, 0, 6, 12]) == 4
    for _ in range(300):
        a = [random.randint(0, 9) for _ in range(random.randint(2, 10))]
        want = next((i for i in range(1, len(a)) if max(a[:i]) <= min(a[i:])), -1)
        assert partition_disjoint(a) == want


def test_max_sum_two_no_overlap_matches_brute_force():
    random.seed(55)
    assert max_sum_two_no_overlap([0, 6, 5, 2, 2, 5, 1, 9, 4], 1, 2) == 20
    assert max_sum_two_no_overlap([3, 8, 1, 3, 2, 1, 8, 9, 0], 3, 2) == 29
    for _ in range(300):
        n = random.randint(2, 10)
        L = random.randint(1, n - 1)
        M = random.randint(1, n - L)
        a = [random.randint(-5, 9) for _ in range(n)]
        want = float("-inf")
        for i in range(n - L + 1):
            for j in range(n - M + 1):
                if i + L <= j or j + M <= i:
                    want = max(want, sum(a[i:i + L]) + sum(a[j:j + M]))
        assert max_sum_two_no_overlap(a, L, M) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
