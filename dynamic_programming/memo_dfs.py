"""DFS + memoisation on implicit DAGs — longest increasing path in a grid.

Signs: moves in any direction, but a strict ordering (strictly increasing
       values, decreasing heights, fewer remaining steps) means you can never
       come back, so the move graph is a DAG. "Longest path" on it.
Approach: f(cell) = 1 + max f(next) over valid moves. The strict order
          guarantees f never calls itself back, so plain @cache is safe and
          each cell is solved once. Equivalent bottom-up: process cells in
          decreasing value order — that *is* a topological order — and no
          recursion is needed.
Complexity: O(R * C) states, 4 transitions each; O(R * C log(R * C)) for the
            sorted bottom-up version.
Gotchas:
  - With a non-strict order (>=), equal neighbours form cycles and the memo
    returns garbage or recurses forever. Memoised DFS is only DP on a DAG.
  - Recursion depth equals the longest path, which can be R * C on a snake
    grid. The recursive version raises the limit; the sorted version never
    recurses and is the one to use on big inputs.
  - Longest path in a general graph (with cycles) is NP-hard — the DAG
    property is doing all the work.

Run the tests at the bottom with:  python3 dynamic_programming/memo_dfs.py
"""

import random
import sys
from functools import cache


DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


# ---------------------------------------------------------------- implementation


def longest_increasing_path(m):
    """Longest strictly increasing 4-directional path, memoised DFS."""
    if not m or not m[0]:
        return 0
    R, C = len(m), len(m[0])
    sys.setrecursionlimit(max(sys.getrecursionlimit(), R * C + 100))

    @cache
    def f(r, c):
        return 1 + max(
            (f(nr, nc)
             for nr, nc in ((r + dr, c + dc) for dr, dc in DIRS)
             if 0 <= nr < R and 0 <= nc < C and m[nr][nc] > m[r][c]),
            default=0,
        )

    return max(f(r, c) for r in range(R) for c in range(C))


def longest_increasing_path_sorted(m):
    """Same answer with no recursion: fill cells from the largest value down.

    Every valid move goes to a strictly larger value, so by the time a cell is
    processed all of its successors are final.
    """
    if not m or not m[0]:
        return 0
    R, C = len(m), len(m[0])
    best = [[1] * C for _ in range(R)]
    for v, r, c in sorted(((m[r][c], r, c) for r in range(R) for c in range(C)), reverse=True):
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and m[nr][nc] > v:
                best[r][c] = max(best[r][c], best[nr][nc] + 1)
    return max(map(max, best))


# ------------------------------------------------------------------------ tests


def brute_longest(m):
    """Explicit DFS over every simple increasing path — exponential, no memo."""
    R, C = len(m), len(m[0])

    def walk(r, c):
        return 1 + max(
            (walk(r + dr, c + dc) for dr, dc in DIRS
             if 0 <= r + dr < R and 0 <= c + dc < C and m[r + dr][c + dc] > m[r][c]),
            default=0,
        )

    return max(walk(r, c) for r in range(R) for c in range(C))


def test_classic():
    m1 = [[9, 9, 4], [6, 6, 8], [2, 1, 1]]
    m2 = [[3, 4, 5], [3, 2, 6], [2, 2, 1]]
    for fn in (longest_increasing_path, longest_increasing_path_sorted):
        assert fn(m1) == 4  # 1 -> 2 -> 6 -> 9
        assert fn(m2) == 4  # 3 -> 4 -> 5 -> 6
        assert fn([[1]]) == 1
        assert fn([]) == 0
        assert fn([[7, 7], [7, 7]]) == 1  # equal values never extend a path


def test_matches_brute_force():
    random.seed(60)
    for _ in range(200):
        R, C = random.randint(1, 4), random.randint(1, 4)
        m = [[random.randint(0, 6) for _ in range(C)] for _ in range(R)]
        expected = brute_longest(m)
        assert longest_increasing_path(m) == expected
        assert longest_increasing_path_sorted(m) == expected


def test_snake_grid_is_one_long_path():
    # Boustrophedon numbering: the whole grid is a single increasing path.
    R, C = 60, 60
    m = [[r * C + (c if r % 2 == 0 else C - 1 - c) for c in range(C)] for r in range(R)]
    assert longest_increasing_path_sorted(m) == R * C
    assert longest_increasing_path(m) == R * C  # depth 3600, limit raised


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
