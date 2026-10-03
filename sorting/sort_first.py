"""Sort first — sorting as preprocessing, plus pigeonhole when O(n) is required.

Signs: intervals (merge, overlap, can attend), "minimum difference between
       any two", pairs/closest values, H-index, greedy matching (cookies,
       boats), "the answer doesn't depend on input order". If O(n) is
       demanded: maximum gap, H-index -> buckets/counting.
Approach: sorting puts related items next to each other, so global questions
          become adjacent-pair questions. Min difference: only neighbours can
          be closest. Intervals: sort by start, then one sweep.
          Pigeonhole (maximum gap): n numbers in [lo, hi] -> n - 1 buckets of
          width ceil((hi - lo) / (n - 1)). The max gap is at least that width,
          so it never lies inside a bucket: compare each bucket's min with the
          previous non-empty bucket's max.
          Meeting rooms II (min-heap of end times): stacks_heaps/heap_scheduling.py.
Complexity: O(n log n) for the sort, O(n) for the sweep. Maximum gap and
            H-index by counting: O(n).
Gotchas:
  - Merge intervals: overlap test is start <= last_end (touching merges).
    Use max(last_end, end): a later interval may sit inside the last one.
  - Sort a copy if the caller needs the original order (or indices).
  - H-index: h = max i such that the i-th largest citation >= i; counting
    caps citations at n.
  - Maximum gap with < 2 numbers is 0; all-equal -> 0 (avoid width 0).

Run the tests at the bottom with:  python3 sorting/sort_first.py
"""

import random


# ---------------------------------------------------------------- implementation


def merge_intervals(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def can_attend_all(intervals):
    """Meeting rooms I: no two [s, e) overlap. Sort by start, check neighbours."""
    iv = sorted(intervals)
    return all(iv[i][1] <= iv[i + 1][0] for i in range(len(iv) - 1))


def min_abs_difference_pairs(arr):
    """All pairs [a, b] (a < b) with the minimum absolute difference."""
    a = sorted(arr)
    best = min((a[i + 1] - a[i] for i in range(len(a) - 1)), default=None)
    return [[a[i], a[i + 1]] for i in range(len(a) - 1) if a[i + 1] - a[i] == best]


def h_index_sort(citations):
    c = sorted(citations, reverse=True)
    h = 0
    while h < len(c) and c[h] >= h + 1:
        h += 1
    return h


def h_index_counting(citations):
    """O(n): count papers per citation value, capping at n."""
    n = len(citations)
    count = [0] * (n + 1)
    for x in citations:
        count[min(x, n)] += 1
    papers = 0
    for h in range(n, -1, -1):
        papers += count[h]        # papers with >= h citations
        if papers >= h:
            return h
    return 0


def maximum_gap(nums):
    """Max difference between neighbours in sorted order, in O(n)."""
    n = len(nums)
    if n < 2:
        return 0
    lo, hi = min(nums), max(nums)
    if lo == hi:
        return 0
    width = max(1, (hi - lo) // (n - 1))
    k = (hi - lo) // width + 1
    bmin, bmax = [None] * k, [None] * k
    for x in nums:
        b = (x - lo) // width
        bmin[b] = x if bmin[b] is None else min(bmin[b], x)
        bmax[b] = x if bmax[b] is None else max(bmax[b], x)
    best, prev = 0, lo
    for b in range(k):
        if bmin[b] is not None:
            best = max(best, bmin[b] - prev)
            prev = bmax[b]
    return best


def assign_cookies(greed, sizes):
    """Max children content: sort both, give the smallest cookie that fits."""
    g, s = sorted(greed), sorted(sizes)
    i = 0
    for size in s:
        if i < len(g) and size >= g[i]:
            i += 1
    return i


# ------------------------------------------------------------------------ tests


def test_merge_intervals_matches_point_cover():
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]
    assert merge_intervals([[1, 10], [2, 3], [4, 5]]) == [[1, 10]]
    assert merge_intervals([]) == []
    random.seed(51)
    for _ in range(200):
        iv = []
        for _ in range(random.randint(0, 8)):
            s = random.randint(0, 20)
            iv.append([s, s + random.randint(0, 5)])
        got = merge_intervals(iv)
        # brute force on half-points: covered set must match, and outputs are disjoint
        def covered(ivs):
            return {x / 2 for s, e in ivs for x in range(2 * s, 2 * e + 1)}
        assert covered(got) == covered(iv)
        assert all(got[i][1] < got[i + 1][0] for i in range(len(got) - 1))


def test_can_attend_all():
    assert can_attend_all([[0, 30], [5, 10], [15, 20]]) is False
    assert can_attend_all([[7, 10], [2, 4]]) is True
    assert can_attend_all([]) is True
    random.seed(52)
    for _ in range(200):
        iv = []
        for _ in range(random.randint(0, 5)):
            s = random.randint(0, 20)
            iv.append([s, s + random.randint(1, 5)])
        brute = all(a[1] <= b[0] or b[1] <= a[0]
                    for i, a in enumerate(iv) for b in iv[i + 1:])
        assert can_attend_all(iv) == brute


def test_min_abs_difference_pairs():
    assert min_abs_difference_pairs([4, 2, 1, 3]) == [[1, 2], [2, 3], [3, 4]]
    random.seed(53)
    for _ in range(200):
        a = random.sample(range(-50, 50), random.randint(2, 15))  # distinct
        best = min(abs(x - y) for i, x in enumerate(a) for y in a[i + 1:])
        brute = sorted([min(x, y), max(x, y)] for i, x in enumerate(a)
                       for y in a[i + 1:] if abs(x - y) == best)
        assert min_abs_difference_pairs(a) == brute


def test_h_index_both_ways_match_definition():
    assert h_index_sort([3, 0, 6, 1, 5]) == 3
    assert h_index_counting([1, 3, 1]) == 1
    random.seed(54)
    for _ in range(300):
        c = [random.randint(0, 12) for _ in range(random.randint(0, 12))]
        brute = max(h for h in range(len(c) + 1) if sum(x >= h for x in c) >= h)
        assert h_index_sort(c) == brute == h_index_counting(c)


def test_maximum_gap_matches_sort():
    assert maximum_gap([3, 6, 9, 1]) == 3
    assert maximum_gap([10]) == 0
    assert maximum_gap([]) == 0
    assert maximum_gap([5, 5, 5]) == 0
    random.seed(55)
    for _ in range(300):
        a = [random.randint(-100, 10**6 * random.randint(0, 1) + 100)
             for _ in range(random.randint(2, 30))]
        s = sorted(a)
        assert maximum_gap(a) == max(s[i + 1] - s[i] for i in range(len(s) - 1))


def test_assign_cookies_matches_brute_force():
    assert assign_cookies([1, 2, 3], [1, 1]) == 1
    assert assign_cookies([1, 2], [1, 2, 3]) == 2
    random.seed(56)
    for _ in range(200):
        g = [random.randint(1, 6) for _ in range(random.randint(0, 5))]
        s = [random.randint(1, 6) for _ in range(random.randint(0, 5))]
        # brute force: try every assignment of cookies to children
        best = 0

        def go(i, used, cnt):
            nonlocal best
            best = max(best, cnt)
            if i == len(g):
                return
            go(i + 1, used, cnt)
            for j in range(len(s)):
                if not used >> j & 1 and s[j] >= g[i]:
                    go(i + 1, used | 1 << j, cnt + 1)

        go(0, 0, 0)
        assert assign_cookies(g, s) == best


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
