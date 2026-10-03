"""Interval relations — covered intervals, points in intervals, smallest cover.

Signs: "remove intervals covered by another", "how many intervals contain
       each point", "smallest interval containing each query", many queries
       against a fixed set of intervals.
Approach:
  - Covered: sort by start ascending, end DESCENDING. Then an interval is
    covered iff its end <= the max end seen so far.
  - Count containing x: #starts <= x minus #ends < x, two bisects over the
    sorted starts and sorted ends. No per-interval loop per query.
  - Smallest containing x (offline): sort queries. Sweep x upward, push every
    interval with start <= x into a min-heap by size, pop tops that end
    before x. The top is the answer. Each interval is pushed and popped once.
Complexity: covered O(n log n); counting O((n + q) log n); smallest
            O((n + q) log n).
Gotchas:
  - Covered ties: [1, 4] and [1, 6] share a start. Without end descending,
    [1, 4] comes first and isn't flagged.
  - All three use closed [s, e]: x == e counts as inside. For half-open,
    count with bisect_right(ends, x) instead of bisect_left.
  - Offline queries: remember each query's original index before sorting.
  - Intersections of two sorted interval lists: sliding_window/merge_two.py.

Run the tests at the bottom with:  python3 intervals/relations.py
"""

import heapq
from bisect import bisect_left, bisect_right


# ---------------------------------------------------------------- implementation


def remove_covered_intervals(intervals):
    """LC 1288. Count intervals not covered by another ([c, d] covers [a, b]
    iff c <= a and b <= d)."""
    kept, max_end = 0, float("-inf")
    for _, e in sorted(intervals, key=lambda x: (x[0], -x[1])):
        if e > max_end:                        # sticks out past everything earlier
            kept += 1
            max_end = e
    return kept


def count_containing(intervals, points):
    """For each point x, how many closed intervals contain it."""
    starts = sorted(s for s, _ in intervals)
    ends = sorted(e for _, e in intervals)
    return [bisect_right(starts, x) - bisect_left(ends, x) for x in points]


def min_interval(intervals, queries):
    """LC 1851. Size (e - s + 1) of the smallest interval containing each
    query, or -1."""
    iv = sorted(intervals)
    ans = [-1] * len(queries)
    heap, i = [], 0                            # (size, end)
    for q, idx in sorted((q, k) for k, q in enumerate(queries)):
        while i < len(iv) and iv[i][0] <= q:
            s, e = iv[i]
            heapq.heappush(heap, (e - s + 1, e))
            i += 1
        while heap and heap[0][1] < q:         # ended before q: useless forever
            heapq.heappop(heap)
        if heap:
            ans[idx] = heap[0][0]
    return ans


# ------------------------------------------------------------------------ tests


def _rand_intervals(rng, n, hi=20):
    out = []
    for _ in range(n):
        a = rng.randint(0, hi)
        out.append([a, a + rng.randint(0, 6)])
    return out


def test_examples():
    assert remove_covered_intervals([[1, 4], [3, 6], [2, 8]]) == 2
    assert remove_covered_intervals([[1, 4], [1, 6]]) == 1        # shared start
    assert count_containing([[1, 3], [2, 5], [5, 6]], [0, 2, 5, 7]) == [0, 2, 2, 0]
    assert min_interval([[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5]) == [3, 3, 1, 4]
    assert min_interval([[2, 3], [2, 5], [1, 8], [20, 25]], [2, 19, 5, 22]) == [2, -1, 4, 6]


def test_covered_matches_pairwise():
    import random

    rng = random.Random(1)
    for _ in range(500):
        iv = [list(x) for x in {tuple(x) for x in _rand_intervals(rng, rng.randint(0, 8))}]
        brute = sum(not any(j != i and c <= a and b <= d for j, (c, d) in enumerate(iv))
                    for i, (a, b) in enumerate(iv))
        assert remove_covered_intervals(iv) == brute


def test_queries_match_direct_scan():
    import random

    rng = random.Random(2)
    for _ in range(500):
        iv = _rand_intervals(rng, rng.randint(0, 8))
        qs = [rng.randint(-2, 28) for _ in range(rng.randint(0, 8))]
        assert count_containing(iv, qs) == [sum(s <= x <= e for s, e in iv) for x in qs]
        assert min_interval(iv, qs) == [
            min((e - s + 1 for s, e in iv if s <= x <= e), default=-1) for x in qs]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
