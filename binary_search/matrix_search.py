"""2D matrix search — flatten when rows chain, staircase when only rows and columns sort.

Signs: "search a 2D matrix", "each row sorted and first of a row > last of
       the previous" (fully sorted), "rows sorted and columns sorted" (only
       partially sorted), "count elements <= x in a sorted matrix".
Approach:
  - Fully sorted (row-major): it IS a sorted array of R * C items. Binary
    search index i and read m[i // C][i % C].
  - Rows and columns sorted: staircase. Start top-right. Too big -> move
    left (the whole column below is bigger too). Too small -> move down (the
    whole row to the left is smaller too). Each step discards a row or column.
  - Counting <= x uses the same staircase walk from bottom-left.
Complexity: flatten O(log(R * C)); staircase O(R + C); row-by-row bisect
            O(R log C) — better than staircase only when R is much smaller than C.
Gotchas:
  - Flatten is WRONG on a merely row-and-column-sorted matrix:
    [[1, 4], [2, 5]] read row-major is 1, 4, 2, 5.
  - Staircase must start at a corner where one direction grows and the
    other shrinks: top-right or bottom-left. Top-left gives no decision.
  - Empty matrix / empty rows: guard before m[0].

Run the tests at the bottom with:  python3 binary_search/matrix_search.py
"""

from bisect import bisect_left, bisect_right


# ---------------------------------------------------------------- implementation


def search_sorted_matrix(m, target):
    """Row-major sorted matrix (each row starts above the previous row's end)."""
    if not m or not m[0]:
        return False
    R, C = len(m), len(m[0])
    lo, hi = 0, R * C
    while lo < hi:                     # lower_bound over the virtual flat array
        mid = (lo + hi) // 2
        if m[mid // C][mid % C] >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo < R * C and m[lo // C][lo % C] == target


def search_staircase(m, target):
    """Rows sorted left-to-right, columns sorted top-to-bottom. Returns (r, c) or None."""
    if not m or not m[0]:
        return None
    r, c = 0, len(m[0]) - 1            # top-right corner
    while r < len(m) and c >= 0:
        v = m[r][c]
        if v == target:
            return r, c
        if v > target:
            c -= 1                     # everything below in column c is >= v
        else:
            r += 1                     # everything left in row r is <= v
    return None


def search_rows_bisect(m, target):
    """Alternative for row-sorted matrices: bisect each row. O(R log C)."""
    for row in m:
        i = bisect_left(row, target)
        if i < len(row) and row[i] == target:
            return True
    return False


def count_leq(m, x):
    """Number of cells <= x in a row-and-column-sorted matrix. O(R + C).

    Walk from bottom-left: if m[r][c] <= x the whole column above it counts.
    """
    R, C = len(m), len(m[0])
    r, c, count = R - 1, 0, 0
    while r >= 0 and c < C:
        if m[r][c] <= x:
            count += r + 1
            c += 1
        else:
            r -= 1
    return count


# ------------------------------------------------------------------------ tests


def _random_sorted_matrix(rng, R, C):
    vals = sorted(rng.sample(range(-100, 100), R * C))
    return [vals[i * C:(i + 1) * C] for i in range(R)]


def _random_young_tableau(rng, R, C):
    """Rows and columns non-decreasing, but not row-major sorted in general."""
    m = [[0] * C for _ in range(R)]
    for r in range(R):
        for c in range(C):
            floor = max(m[r - 1][c] if r else 0, m[r][c - 1] if c else 0)
            m[r][c] = floor + rng.randint(0, 3)
    return m


def test_flatten_matches_membership():
    import random

    rng = random.Random(60)
    for _ in range(300):
        m = _random_sorted_matrix(rng, rng.randint(1, 5), rng.randint(1, 5))
        flat = {v for row in m for v in row}
        for t in range(-102, 102, 3):
            assert search_sorted_matrix(m, t) == (t in flat)
    assert search_sorted_matrix([], 1) is False
    assert search_sorted_matrix([[]], 1) is False


def test_staircase_matches_membership_and_bisect():
    import random

    rng = random.Random(61)
    for _ in range(300):
        m = _random_young_tableau(rng, rng.randint(1, 6), rng.randint(1, 6))
        cells = {v for row in m for v in row}
        for t in range(-1, max(cells) + 2):
            hit = search_staircase(m, t)
            assert (hit is not None) == (t in cells) == search_rows_bisect(m, t)
            if hit:
                assert m[hit[0]][hit[1]] == t


def test_flatten_is_wrong_on_young_tableau():
    m = [[1, 4], [2, 5]]
    assert search_staircase(m, 2) == (1, 0)
    assert search_sorted_matrix(m, 2) is False  # the documented trap


def test_count_leq_matches_brute_force():
    import random

    rng = random.Random(62)
    for _ in range(300):
        m = _random_young_tableau(rng, rng.randint(1, 6), rng.randint(1, 6))
        for x in range(-1, m[-1][-1] + 2):
            assert count_leq(m, x) == sum(v <= x for row in m for v in row)
            assert count_leq(m, x) == sum(bisect_right(row, x) for row in m)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
