"""Diagonals — group cells by r + c or r - c, zigzag traversal, diagonal checks.

Signs: "diagonal order", "zigzag", "sort each diagonal", "every diagonal has
       the same value" (Toeplitz), "sum of both diagonals", N-Queens-style
       "same diagonal" tests.
Approach: two keys name every diagonal.
    r + c  constant along an anti-diagonal  (/), keys 0 .. R+C-2
    r - c  constant along a diagonal        (\\), keys -(C-1) .. R-1
  Group by the key, then read each group in the order the problem wants.
  Zigzag (Diagonal Traverse): anti-diagonal s runs r = max(0, s-C+1) ..
  min(s, R-1); read it upward (r falling) when s is even, downward when odd.
Complexity: O(R C) time. Grouping uses O(R C) extra; the zigzag index loop
            uses O(1) beyond the output. Sorting diagonals: O(R C log min(R, C)).
Gotchas:
  - r - c is negative for the upper-right diagonals. Use a dict, or offset by
    C - 1 for a list index.
  - The row bounds of anti-diagonal s: start at max(0, s - C + 1), not 0.
  - Diagonal sum on odd n: the centre is on both diagonals; count it once.
  - Board diagonals for N-Queens use the same keys - see
    backtracking/constraint_placement.py for the full search.

Run the tests at the bottom with:  python3 matrix_simulation/diagonals.py
"""

import random
from collections import defaultdict


# ---------------------------------------------------------------- implementation


def anti_diagonals(m):
    """{r + c: [values top to bottom]} — each list runs down-left."""
    groups = defaultdict(list)
    for r, row in enumerate(m):
        for c, x in enumerate(row):
            groups[r + c].append(x)
    return dict(groups)


def diagonals(m):
    """{r - c: [values top to bottom]} — each list runs down-right."""
    groups = defaultdict(list)
    for r, row in enumerate(m):
        for c, x in enumerate(row):
            groups[r - c].append(x)
    return dict(groups)


def diagonal_traverse(m):
    """Diagonal Traverse: zigzag from (0, 0), first move up-right."""
    if not m or not m[0]:
        return []
    R, C = len(m), len(m[0])
    out = []
    for s in range(R + C - 1):
        lo, hi = max(0, s - C + 1), min(s, R - 1)
        rows = range(hi, lo - 1, -1) if s % 2 == 0 else range(lo, hi + 1)
        out.extend(m[r][s - r] for r in rows)
    return out


def diagonal_traverse_walk(m):
    """Same zigzag, walked cell by cell with the bounce rules.

    Going up-right and blocked: step right if possible, else down. Going
    down-left and blocked: step down if possible, else right. Then flip.
    """
    if not m or not m[0]:
        return []
    R, C = len(m), len(m[0])
    out, r, c, up = [], 0, 0, True
    for _ in range(R * C):
        out.append(m[r][c])
        if up:
            if r > 0 and c < C - 1:
                r, c = r - 1, c + 1
            else:
                if c < C - 1:
                    c += 1
                else:
                    r += 1
                up = False
        else:
            if r < R - 1 and c > 0:
                r, c = r + 1, c - 1
            else:
                if r < R - 1:
                    r += 1
                else:
                    c += 1
                up = True
    return out


def find_diagonal_order_jagged(rows):
    """Diagonal Traverse II: jagged rows; each anti-diagonal read bottom-left
    to top-right. Only real cells are touched, so no R x maxC scan."""
    groups = defaultdict(list)
    for r, row in enumerate(rows):
        for c, x in enumerate(row):
            groups[r + c].append(x)  # appended top to bottom
    out = []
    for s in sorted(groups):
        out.extend(reversed(groups[s]))
    return out


def sort_diagonally(m):
    """Sort the Matrix Diagonally: each \\ diagonal ascending, top-left first."""
    R, C = len(m), len(m[0])
    groups = diagonals(m)
    for k in groups:
        groups[k].sort(reverse=True)  # pop() from the end gives smallest first
    out = [[0] * C for _ in range(R)]
    for r in range(R):
        for c in range(C):
            out[r][c] = groups[r - c].pop()
    return out


def diagonal_sum(m):
    """Matrix Diagonal Sum: primary + secondary, centre once."""
    n = len(m)
    total = sum(m[i][i] + m[i][n - 1 - i] for i in range(n))
    if n % 2:
        total -= m[n // 2][n // 2]
    return total


def is_toeplitz(m):
    """Toeplitz Matrix: every cell equals its up-left neighbour.

    Streaming follow-up (one row in memory): compare row[:-1] with next[1:].
    """
    return all(m[r][c] == m[r - 1][c - 1] for r in range(1, len(m)) for c in range(1, len(m[0])))


# ------------------------------------------------------------------------ tests


def random_shapes(rng, count=40, max_side=7):
    shapes = [(1, 1), (1, 6), (6, 1), (2, 5), (5, 2)]
    return shapes + [(rng.randint(1, max_side), rng.randint(1, max_side)) for _ in range(count)]


def test_groups_partition_the_cells():
    rng = random.Random(20)
    for R, C in random_shapes(rng):
        m = [[r * C + c for c in range(C)] for r in range(R)]
        a, d = anti_diagonals(m), diagonals(m)
        assert sorted(a) == list(range(R + C - 1))
        assert sorted(d) == list(range(-(C - 1), R))
        assert sorted(x for g in a.values() for x in g) == list(range(R * C))
        for s, g in a.items():  # each anti-diagonal really steps down-left
            cells = [divmod(x, C) for x in g]
            assert all(r + c == s for r, c in cells)
            assert all(b[0] == a_[0] + 1 and b[1] == a_[1] - 1 for a_, b in zip(cells, cells[1:]))


def test_zigzag_index_loop_matches_walk_and_sort():
    rng = random.Random(21)
    for R, C in random_shapes(rng):
        m = [[rng.randint(0, 99) for _ in range(C)] for _ in range(R)]
        cells = [(r, c) for r in range(R) for c in range(C)]
        # brute force: order by diagonal, then row falling on even, rising on odd
        cells.sort(key=lambda rc: (rc[0] + rc[1], -rc[0] if (rc[0] + rc[1]) % 2 == 0 else rc[0]))
        expected = [m[r][c] for r, c in cells]
        assert diagonal_traverse(m) == expected
        assert diagonal_traverse_walk(m) == expected


def test_zigzag_example():
    assert diagonal_traverse([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 4, 7, 5, 3, 6, 8, 9]


def test_jagged_matches_sort():
    rng = random.Random(22)
    for _ in range(50):
        rows = [[rng.randint(0, 99) for _ in range(rng.randint(1, 6))] for _ in range(rng.randint(1, 6))]
        cells = [(r, c) for r, row in enumerate(rows) for c in range(len(row))]
        cells.sort(key=lambda rc: (rc[0] + rc[1], -rc[0]))
        assert find_diagonal_order_jagged(rows) == [rows[r][c] for r, c in cells]


def test_sort_diagonally_against_walk_each_diagonal():
    rng = random.Random(23)
    for R, C in random_shapes(rng):
        m = [[rng.randint(0, 20) for _ in range(C)] for _ in range(R)]
        out = sort_diagonally(m)
        starts = [(0, c) for c in range(C)] + [(r, 0) for r in range(1, R)]
        for r0, c0 in starts:
            path = []
            r, c = r0, c0
            while r < R and c < C:
                path.append((r, c))
                r, c = r + 1, c + 1
            assert [out[r][c] for r, c in path] == sorted(m[r][c] for r, c in path)


def test_diagonal_sum_brute():
    rng = random.Random(24)
    for n in range(1, 9):
        m = [[rng.randint(-5, 9) for _ in range(n)] for _ in range(n)]
        brute = sum(m[r][c] for r in range(n) for c in range(n) if r == c or r + c == n - 1)
        assert diagonal_sum(m) == brute


def test_toeplitz_matches_grouping():
    rng = random.Random(25)
    for R, C in random_shapes(rng, 80):
        seed = [rng.randint(0, 2) for _ in range(R + C)]
        m = [[seed[r - c + C] for c in range(C)] for r in range(R)]  # Toeplitz by construction
        if rng.random() < 0.5:
            m[rng.randrange(R)][rng.randrange(C)] = rng.randint(0, 2)  # maybe break it
        expected = all(len(set(g)) == 1 for g in diagonals(m).values())
        assert is_toeplitz(m) == expected


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
