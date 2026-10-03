"""Difference arrays — many range updates in O(1) each, one prefix sum to read.

Signs: "add v to every element in [l, r]" many times, then read the array;
       passengers on/off a car, flight bookings, meeting overlap, covering a
       grid with stamps, "is any point over capacity".
Approach: the inverse of a prefix sum. Store d[i] = a[i] - a[i-1]. Adding v
          to a[l..r] touches only d[l] += v and d[r + 1] -= v. A prefix sum of
          d rebuilds a. In 2D, a rectangle update touches four corners:
            d[r1][c1] += v, d[r1][c2+1] -= v, d[r2+1][c1] -= v, d[r2+1][c2+1] += v
          and a 2D prefix sum rebuilds the grid.
Complexity: O(1) per update (O(1) per rectangle), O(n) (O(R C)) to rebuild.
Gotchas:
  - Size n + 1 so d[r + 1] never overflows the end.
  - Half-open vs inclusive: car pooling drops passengers AT `to` (minus at
    to); flight bookings are inclusive and 1-indexed (minus at last + 1).
  - Huge or sparse coordinates (1e9) -> a Counter of events, then walk the
    keys in sorted order (a sweep line).
  - Updates and reads interleave -> Fenwick tree on the difference array
    (fenwick.RangeAddFenwick).

Run the tests at the bottom with:  python3 prefix_sums/difference_array.py
"""

import random
from collections import Counter
from itertools import accumulate


# ---------------------------------------------------------------- implementation


def range_add(n, updates):
    """Apply (l, r, v) = "add v to a[l..r]" to a zero array of length n."""
    d = [0] * (n + 1)
    for l, r, v in updates:
        d[l] += v
        d[r + 1] -= v
    return list(accumulate(d[:n]))


def car_pooling(trips, capacity):
    """(people, frm, to): board at frm, leave at to. Never over capacity?"""
    d = [0] * (max((t for _, _, t in trips), default=0) + 1)
    for people, frm, to in trips:
        d[frm] += people
        d[to] -= people              # gone at `to`, so the seat is free there
    load = 0
    for x in d:
        load += x
        if load > capacity:
            return False
    return True


def corp_flight_bookings(bookings, n):
    """(first, last, seats) on flights first..last, 1-indexed inclusive."""
    return range_add(n, [(f - 1, l - 1, s) for f, l, s in bookings])


def max_overlap(intervals):
    """Most half-open intervals [s, e) covering one point (min meeting rooms).

    Coordinates can be huge, so diff into a Counter and sweep sorted keys.
    """
    events = Counter()
    for s, e in intervals:
        events[s] += 1
        events[e] -= 1
    best = cur = 0
    for x in sorted(events):
        cur += events[x]
        best = max(best, cur)
    return best


def range_add_2d(R, C, updates):
    """Apply (r1, c1, r2, c2, v) rectangle adds to a zero R x C grid."""
    d = [[0] * (C + 1) for _ in range(R + 1)]
    for r1, c1, r2, c2, v in updates:
        d[r1][c1] += v
        d[r1][c2 + 1] -= v
        d[r2 + 1][c1] -= v
        d[r2 + 1][c2 + 1] += v
    for r in range(R):                       # 2D prefix sum, in place
        for c in range(C):
            d[r][c] += (d[r - 1][c] if r else 0) + (d[r][c - 1] if c else 0) \
                - (d[r - 1][c - 1] if r and c else 0)
    return [row[:C] for row in d[:R]]


def possible_to_stamp(grid, h, w):
    """Stamping the Grid: cover every 0 with h x w stamps that avoid every 1?

    1. A 2D prefix sum of the 1s says in O(1) whether a stamp fits at (r, c).
    2. A 2D difference array adds +1 over every stamp placed.
    3. Rebuild coverage; every 0 must be covered at least once.
    Placing every stamp that fits is safe: stamps may overlap.
    """
    R, C = len(grid), len(grid[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for r in range(R):
        for c in range(C):
            P[r + 1][c + 1] = grid[r][c] + P[r][c + 1] + P[r + 1][c] - P[r][c]
    stamps = []
    for r in range(R - h + 1):
        for c in range(C - w + 1):
            r2, c2 = r + h, c + w
            if P[r2][c2] - P[r][c2] - P[r2][c] + P[r][c] == 0:
                stamps.append((r, c, r2 - 1, c2 - 1, 1))
    cover = range_add_2d(R, C, stamps)
    return all(grid[r][c] or cover[r][c] for r in range(R) for c in range(C))


# ------------------------------------------------------------------------ tests


def test_range_add_matches_brute_force():
    random.seed(41)
    assert range_add(5, [(1, 3, 2), (2, 4, 3), (0, 2, -2)]) == [-2, 0, 3, 5, 3]
    for _ in range(200):
        n = random.randint(1, 12)
        ups = []
        for _ in range(random.randint(0, 8)):
            l = random.randrange(n)
            ups.append((l, random.randint(l, n - 1), random.randint(-5, 5)))
        want = [0] * n
        for l, r, v in ups:
            for i in range(l, r + 1):
                want[i] += v
        assert range_add(n, ups) == want


def test_car_pooling_matches_brute_force():
    random.seed(42)
    assert car_pooling([[2, 1, 5], [3, 3, 7]], 4) is False
    assert car_pooling([[2, 1, 5], [3, 3, 7]], 5) is True
    assert car_pooling([[2, 1, 5], [3, 5, 7]], 3) is True   # drop-off frees the seat
    for _ in range(300):
        trips = []
        for _ in range(random.randint(1, 6)):
            f = random.randint(0, 9)
            trips.append((random.randint(1, 5), f, random.randint(f + 1, 10)))
        cap = random.randint(1, 12)
        want = all(sum(p for p, f, t in trips if f <= x < t) <= cap for x in range(11))
        assert car_pooling(trips, cap) is want


def test_corp_flight_bookings_example():
    assert corp_flight_bookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5) == [10, 55, 45, 25, 25]
    assert corp_flight_bookings([[1, 2, 10], [2, 2, 15]], 2) == [10, 25]


def test_max_overlap_matches_brute_force():
    random.seed(43)
    assert max_overlap([(0, 30), (5, 10), (15, 20)]) == 2
    assert max_overlap([(1, 5), (5, 10)]) == 1                  # touching is not overlap
    assert max_overlap([(10**9, 10**9 + 5), (10**9 + 1, 10**9 + 2)]) == 2
    for _ in range(300):
        ivs = []
        for _ in range(random.randint(0, 7)):
            s = random.randint(0, 15)
            ivs.append((s, random.randint(s + 1, 20)))
        want = max((sum(s <= x < e for s, e in ivs) for x in range(21)), default=0)
        assert max_overlap(ivs) == want


def test_range_add_2d_matches_brute_force():
    random.seed(44)
    for _ in range(150):
        R, C = random.randint(1, 6), random.randint(1, 6)
        ups = []
        for _ in range(random.randint(0, 6)):
            r1, c1 = random.randrange(R), random.randrange(C)
            ups.append((r1, c1, random.randint(r1, R - 1), random.randint(c1, C - 1),
                        random.randint(-3, 3)))
        want = [[0] * C for _ in range(R)]
        for r1, c1, r2, c2, v in ups:
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    want[r][c] += v
        assert range_add_2d(R, C, ups) == want


def test_possible_to_stamp_matches_brute_force():
    random.seed(45)
    g = [[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]]
    assert possible_to_stamp(g, 4, 3) is True
    g = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    assert possible_to_stamp(g, 2, 2) is False
    for _ in range(200):
        R, C = random.randint(1, 5), random.randint(1, 5)
        g = [[int(random.random() < 0.2) for _ in range(C)] for _ in range(R)]
        h, w = random.randint(1, R), random.randint(1, C)
        covered = [[False] * C for _ in range(R)]
        for r in range(R - h + 1):
            for c in range(C - w + 1):
                cells = [(i, j) for i in range(r, r + h) for j in range(c, c + w)]
                if all(g[i][j] == 0 for i, j in cells):
                    for i, j in cells:
                        covered[i][j] = True
        want = all(g[r][c] or covered[r][c] for r in range(R) for c in range(C))
        assert possible_to_stamp(g, h, w) is want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
