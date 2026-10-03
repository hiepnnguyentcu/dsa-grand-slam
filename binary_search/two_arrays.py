"""Two sorted arrays — median and k-th smallest without merging.

Signs: "median of two sorted arrays", "k-th smallest of two sorted arrays",
       O(log(m + n)) required, merging (O(m + n)) is too slow.
Approach:
  - Partition (median): cut A at i and B at j = half - i so the left side
    holds exactly half the elements. The cut is right when
    A[i-1] <= B[j] and B[j-1] <= A[i]. Binary search i over the SHORTER
    array: A[i-1] > B[j] means i is too far right.
  - Eliminate (k-th): compare A[k/2 - 1] with B[k/2 - 1]. The smaller one
    and everything before it cannot be the k-th — at most k - 2 elements
    are below it. Drop them, reduce k, repeat.
Complexity: partition O(log min(m, n)); k-th elimination O(log k).
Gotchas:
  - Binary search the shorter array, or j = half - i can go negative.
  - Use -inf / +inf for cuts at the edges (i == 0, i == m) instead of
    special cases.
  - half = (m + n + 1) // 2 puts the extra element on the left, so for odd
    totals the median is max(left side).
  - In the k-th version, clamp the step to the array's length:
    i = min(len(A), k // 2).

Run the tests at the bottom with:  python3 binary_search/two_arrays.py
"""


# ---------------------------------------------------------------- implementation

INF = float("inf")


def median_two_sorted(a, b):
    """Median of the union of two sorted arrays (not both empty)."""
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    half = (m + n + 1) // 2
    lo, hi = 0, m                      # i = elements taken from a, in [0, m]
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        a_left = a[i - 1] if i > 0 else -INF
        a_right = a[i] if i < m else INF
        b_left = b[j - 1] if j > 0 else -INF
        b_right = b[j] if j < n else INF
        if a_left > b_right:
            hi = i - 1                 # took too many from a
        elif b_left > a_right:
            lo = i + 1                 # took too few from a
        else:
            left_max = max(a_left, b_left)
            if (m + n) % 2:
                return float(left_max)
            return (left_max + min(a_right, b_right)) / 2
    raise ValueError("inputs must be sorted")


def kth_smallest_two_sorted(a, b, k):
    """k-th smallest (1-based) of the union of two sorted arrays.

    Iterative elimination. Each round discards about k / 2 elements.
    """
    ia = ib = 0                       # a[ia:] and b[ib:] are still in play
    while True:
        if ia == len(a):
            return b[ib + k - 1]
        if ib == len(b):
            return a[ia + k - 1]
        if k == 1:
            return min(a[ia], b[ib])
        step_a = min(len(a) - ia, k // 2)
        step_b = min(len(b) - ib, k // 2)
        if a[ia + step_a - 1] <= b[ib + step_b - 1]:
            ia += step_a              # those step_a items are all below the k-th
            k -= step_a
        else:
            ib += step_b
            k -= step_b


def median_via_kth(a, b):
    """Second implementation of the median, built on kth_smallest_two_sorted."""
    total = len(a) + len(b)
    if total % 2:
        return float(kth_smallest_two_sorted(a, b, total // 2 + 1))
    return (kth_smallest_two_sorted(a, b, total // 2)
            + kth_smallest_two_sorted(a, b, total // 2 + 1)) / 2


# ------------------------------------------------------------------------ tests


def _random_pair(rng):
    a = sorted(rng.randint(-20, 20) for _ in range(rng.randint(0, 10)))
    b = sorted(rng.randint(-20, 20) for _ in range(rng.randint(0, 10)))
    if not a and not b:
        b = [rng.randint(-20, 20)]
    return a, b


def test_median_matches_merge_and_kth_version():
    import random
    import statistics

    rng = random.Random(70)
    for _ in range(2000):
        a, b = _random_pair(rng)
        expected = float(statistics.median(a + b))
        assert median_two_sorted(a, b) == expected
        assert median_via_kth(a, b) == expected


def test_kth_matches_merge():
    import random

    rng = random.Random(71)
    for _ in range(1000):
        a, b = _random_pair(rng)
        merged = sorted(a + b)
        for k in range(1, len(merged) + 1):
            assert kth_smallest_two_sorted(a, b, k) == merged[k - 1]


def test_examples():
    assert median_two_sorted([1, 3], [2]) == 2.0
    assert median_two_sorted([1, 2], [3, 4]) == 2.5
    assert median_two_sorted([], [1]) == 1.0
    assert kth_smallest_two_sorted([2, 3, 6, 7, 9], [1, 4, 8, 10], 5) == 6


def test_very_unequal_lengths():
    a = [5]
    b = list(range(100))
    assert median_two_sorted(a, b) == float(sorted(a + b)[50])
    assert median_two_sorted(b, a) == float(sorted(a + b)[50])


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
