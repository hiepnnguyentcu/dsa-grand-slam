"""2D prefix sums — O(1) rectangle sums, and submatrix problems reduced to 1D.

Signs: "sum of the rectangle (r1, c1)-(r2, c2)" queried many times, block
       sums around every cell, "number of submatrices with sum target",
       "max rectangle sum no larger than k".
Approach: P[r][c] = sum of the r x c block above-left of (r, c), padded with a
          zero row and column. Inclusion-exclusion:
            build:  P[r+1][c+1] = g[r][c] + P[r][c+1] + P[r+1][c] - P[r][c]
            query:  P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
          Submatrix counting: fix a top and bottom row, collapse the strip into
          one array of column sums, run the 1D technique on it.
Complexity: O(R C) build, O(1) per rectangle. Strip reduction: O(R^2 C) for the
            hashmap count, O(R^2 C log C) for "max sum <= k" (sorted prefixes).
Gotchas:
  - Pad to (R+1) x (C+1). Without padding every edge needs its own branch.
  - The query subtracts two strips and adds back the corner subtracted twice.
  - Loop the smaller dimension in the outer pair (swap if R > C).
  - "Max sum <= k" cannot use a hashmap: it needs the smallest earlier prefix
    >= cur - k, i.e. a sorted structure + bisect. insort is O(C) per insert in
    Python; fine for interview sizes, use a balanced tree beyond that.

Run the tests at the bottom with:  python3 prefix_sums/prefix_2d.py
"""

import random
from bisect import bisect_left, insort
from collections import defaultdict


# ---------------------------------------------------------------- implementation


def build_2d(grid):
    """(R+1) x (C+1) prefix table; P[r][c] = sum of grid[:r][:c]."""
    R, C = len(grid), len(grid[0]) if grid else 0
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for r in range(R):
        for c in range(C):
            P[r + 1][c + 1] = grid[r][c] + P[r][c + 1] + P[r + 1][c] - P[r][c]
    return P


def rect_sum(P, r1, c1, r2, c2):
    """Sum of grid[r1..r2][c1..c2], corners inclusive."""
    return P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1]


class NumMatrix:
    """Range Sum Query 2D - Immutable."""

    def __init__(self, matrix):
        self.P = build_2d(matrix)

    def sum_region(self, r1, c1, r2, c2):
        return rect_sum(self.P, r1, c1, r2, c2)


def matrix_block_sum(grid, k):
    """out[r][c] = sum of grid cells within k rows and k columns of (r, c)."""
    R, C = len(grid), len(grid[0])
    P = build_2d(grid)
    return [[rect_sum(P, max(0, r - k), max(0, c - k), min(R - 1, r + k), min(C - 1, c + k))
             for c in range(C)] for r in range(R)]


def num_submatrix_sum_target(grid, target):
    """Number of non-empty submatrices whose sum equals target.

    For each pair of rows (top, bottom), cols[c] = column c summed over the
    strip. Every submatrix in the strip is a subarray of cols, so count
    subarrays with sum target (prefix_hashmap.subarray_sum_count).
    """
    R, C = len(grid), len(grid[0])
    count = 0
    for top in range(R):
        cols = [0] * C
        for bottom in range(top, R):
            for c in range(C):
                cols[c] += grid[bottom][c]
            seen = defaultdict(int)
            seen[0] = 1
            p = 0
            for x in cols:
                p += x
                count += seen[p - target]
                seen[p] += 1
    return count


def max_sum_submatrix(grid, k):
    """Max sum of a submatrix with sum <= k (assumes one exists).

    Same strip reduction. For each prefix cur we want the smallest earlier
    prefix s with s >= cur - k: keep earlier prefixes sorted, bisect.
    """
    if len(grid) > len(grid[0]):                       # outer loop on the short side
        grid = [list(col) for col in zip(*grid)]
    R, C = len(grid), len(grid[0])
    best = float("-inf")
    for top in range(R):
        cols = [0] * C
        for bottom in range(top, R):
            for c in range(C):
                cols[c] += grid[bottom][c]
            seen, cur = [0], 0
            for x in cols:
                cur += x
                i = bisect_left(seen, cur - k)
                if i < len(seen):
                    best = max(best, cur - seen[i])
                insort(seen, cur)
    return best


# ----------------------------------------------------------------- brute force


def _all_rects(R, C):
    for r1 in range(R):
        for r2 in range(r1, R):
            for c1 in range(C):
                for c2 in range(c1, C):
                    yield r1, c1, r2, c2


def _brute_sum(g, r1, c1, r2, c2):
    return sum(g[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1))


def _random_grid(lo, hi):
    R, C = random.randint(1, 5), random.randint(1, 5)
    return [[random.randint(lo, hi) for _ in range(C)] for _ in range(R)]


# ------------------------------------------------------------------------ tests


def test_num_matrix_example():
    m = NumMatrix([[3, 0, 1, 4, 2],
                   [5, 6, 3, 2, 1],
                   [1, 2, 0, 1, 5],
                   [4, 1, 0, 1, 7],
                   [1, 0, 3, 0, 5]])
    assert m.sum_region(2, 1, 4, 3) == 8
    assert m.sum_region(1, 1, 2, 2) == 11
    assert m.sum_region(1, 2, 2, 4) == 12


def test_rect_sum_matches_brute_force():
    random.seed(31)
    for _ in range(100):
        g = _random_grid(-9, 9)
        P = build_2d(g)
        for r1, c1, r2, c2 in _all_rects(len(g), len(g[0])):
            assert rect_sum(P, r1, c1, r2, c2) == _brute_sum(g, r1, c1, r2, c2)


def test_matrix_block_sum_matches_brute_force():
    random.seed(32)
    assert matrix_block_sum([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1) == \
        [[12, 21, 16], [27, 45, 33], [24, 39, 28]]
    for _ in range(100):
        g = _random_grid(0, 9)
        R, C, k = len(g), len(g[0]), random.randint(0, 3)
        want = [[sum(g[i][j] for i in range(R) for j in range(C)
                     if abs(i - r) <= k and abs(j - c) <= k)
                 for c in range(C)] for r in range(R)]
        assert matrix_block_sum(g, k) == want


def test_num_submatrix_sum_target_matches_brute_force():
    random.seed(33)
    assert num_submatrix_sum_target([[0, 1, 0], [1, 1, 1], [0, 1, 0]], 0) == 4
    assert num_submatrix_sum_target([[1, -1], [-1, 1]], 0) == 5
    for _ in range(100):
        g = _random_grid(-2, 2)
        t = random.randint(-2, 2)
        want = sum(_brute_sum(g, *rect) == t for rect in _all_rects(len(g), len(g[0])))
        assert num_submatrix_sum_target(g, t) == want


def test_max_sum_submatrix_matches_brute_force():
    random.seed(34)
    assert max_sum_submatrix([[1, 0, 1], [0, -2, 3]], 2) == 2
    assert max_sum_submatrix([[2, 2, -1]], 3) == 3
    for _ in range(150):
        g = _random_grid(-5, 5)
        sums = [_brute_sum(g, *rect) for rect in _all_rects(len(g), len(g[0]))]
        k = random.choice(sums) + random.randint(0, 3)   # guarantees an answer
        assert max_sum_submatrix(g, k) == max(s for s in sums if s <= k)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
