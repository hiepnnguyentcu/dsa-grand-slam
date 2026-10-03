"""Peak finding and bitonic arrays — search on the slope, not on values.

Signs: "find a peak element", "mountain array", "strictly increasing then
       decreasing", "bitonic", "local maximum", "find in mountain array".
Approach: the array is not sorted, but the comparison a[mid] vs a[mid + 1]
          is a monotone predicate on a mountain ("am I on the way down?").
          Going uphill to the right means a peak exists to the right; downhill
          means one exists at mid or to its left. Generic arrays with
          a[-1] = a[n] = -inf always have such a peak, so the same search finds
          *a* peak, not necessarily the highest.
          Bitonic search = find the peak, then a normal binary search on the
          ascending half and a reversed one on the descending half.
Complexity: O(log n). 2D peak: O(R log C) (binary search columns, scan each).
Gotchas:
  - Compare with mid + 1, and keep mid < hi so mid + 1 is in range:
    `while lo < hi` with hi = n - 1.
  - Plateaus (equal neighbours) break it. a[mid] == a[mid + 1] gives no
    direction. The guarantee needs adjacent values to differ.
  - "A peak" != "the maximum". Only a strict mountain has one peak.
  - Searching the descending half: flip the comparisons, or search -a[i].

Run the tests at the bottom with:  python3 binary_search/peak_finding.py
"""


# ---------------------------------------------------------------- implementation


def find_peak(a):
    """Index of some i with a[i] > both neighbours (edges count as -inf).

    Needs a[i] != a[i + 1]. Works on any such array, not only mountains.
    """
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < a[mid + 1]:
            lo = mid + 1  # uphill to the right: a peak lies right of mid
        else:
            hi = mid      # downhill: mid or something left of it is a peak
    return lo


def search_bitonic(a, target):
    """Smallest index of target in a strict mountain array, or -1.

    Three binary searches: the peak, the ascending side, the descending side.
    The ascending side is checked first, so ties return the smaller index.
    """
    p = find_peak(a)

    lo, hi = 0, p + 1                      # ascending part a[0..p]
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] >= target:
            hi = mid
        else:
            lo = mid + 1
    if lo <= p and a[lo] == target:
        return lo

    lo, hi = p + 1, len(a)                 # descending part a[p+1..]
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= target:               # reversed comparison
            hi = mid
        else:
            lo = mid + 1
    if lo < len(a) and a[lo] == target:
        return lo
    return -1


def find_peak_2d(m):
    """(r, c) of a cell strictly greater than its 4 neighbours. Adjacent cells differ.

    Binary search columns. In column mid, take the row of its maximum. If
    the right neighbour is bigger, a peak exists in the right half (climb
    from there and you can never come back across a column maximum).
    """
    R, C = len(m), len(m[0])
    lo, hi = 0, C - 1
    while lo < hi:
        mid = (lo + hi) // 2
        r = max(range(R), key=lambda i: m[i][mid])
        if m[r][mid] < m[r][mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    r = max(range(R), key=lambda i: m[i][lo])
    return r, lo


# ------------------------------------------------------------------------ tests


def _is_peak(a, i):
    left = a[i - 1] if i > 0 else float("-inf")
    right = a[i + 1] if i + 1 < len(a) else float("-inf")
    return a[i] > left and a[i] > right


def _random_no_equal_neighbours(rng, n):
    a = [rng.randint(0, 9)]
    while len(a) < n:
        v = rng.randint(0, 9)
        if v != a[-1]:
            a.append(v)
    return a


def _random_mountain(rng):
    up = sorted(rng.sample(range(0, 40), rng.randint(1, 8)))
    down = sorted(rng.sample(range(0, up[-1]), min(rng.randint(0, 8), up[-1])), reverse=True)
    return up + down


def test_find_peak_returns_a_peak():
    import random

    rng = random.Random(30)
    for _ in range(1000):
        a = _random_no_equal_neighbours(rng, rng.randint(1, 15))
        assert _is_peak(a, find_peak(a))


def test_mountain_peak_is_the_maximum():
    import random

    rng = random.Random(31)
    for _ in range(500):
        a = _random_mountain(rng)
        assert find_peak(a) == a.index(max(a))


def test_search_bitonic_matches_index():
    import random

    rng = random.Random(32)
    for _ in range(500):
        a = _random_mountain(rng)
        for t in range(-1, 42):
            assert search_bitonic(a, t) == (a.index(t) if t in a else -1)


def test_find_peak_2d_returns_a_peak():
    import random

    rng = random.Random(33)
    for _ in range(300):
        R, C = rng.randint(1, 6), rng.randint(1, 6)
        vals = rng.sample(range(1000), R * C)  # all distinct
        m = [vals[i * C:(i + 1) * C] for i in range(R)]
        r, c = find_peak_2d(m)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                assert m[r][c] > m[nr][nc]


def test_monotone_arrays_peak_at_an_end():
    assert find_peak([1, 2, 3, 4]) == 3
    assert find_peak([4, 3, 2, 1]) == 0
    assert find_peak([7]) == 0


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
