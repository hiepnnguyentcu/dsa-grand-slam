"""Spiral traversal — read a matrix in spiral order, fill one, walk outward.

Signs: "return all elements in spiral order", "generate an n x n matrix filled
       1..n^2 in spiral order", "start at (r0, c0) and walk a clockwise spiral
       that leaves the grid", "layer by layer".
Approach:
  Boundaries (spiral I/II): keep top, bottom, left, right. Walk the top row,
    the right column, then - only if rows and columns remain - the bottom row
    backwards and the left column upwards. Shrink after each side.
  Turning (alternative): one direction index over DIRS4; turn right whenever
    the next cell is out of bounds or already visited. Needs a visited mark.
  Walking outward (spiral III): side lengths go 1, 1, 2, 2, 3, 3, ... Walk the
    unbounded spiral and record only the cells inside the grid.
Complexity: O(R C) time. Boundaries: O(1) extra. Turning: O(R C) for visited.
            Spiral III: O(max(R, C)^2) steps, since it walks off-grid too.
Gotchas:
  - The two `if top <= bottom` / `if left <= right` guards. Without them a
    single remaining row or column is read twice (try 1 x n and n x 1).
  - Spiral III: the side length grows after every second turn, not every turn.
  - Off-grid steps still count as steps; only the recording is skipped.

Run the tests at the bottom with:  python3 matrix_simulation/spiral.py
"""

import random


# ---------------------------------------------------------------- implementation

DIRS4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # E, S, W, N — clockwise


def spiral_order(m):
    """Spiral Matrix: clockwise from (0, 0), boundaries shrinking inward."""
    if not m or not m[0]:
        return []
    out = []
    top, bottom, left, right = 0, len(m) - 1, 0, len(m[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            out.append(m[top][c])
        top += 1
        for r in range(top, bottom + 1):
            out.append(m[r][right])
        right -= 1
        if top <= bottom:  # a bottom row still exists
            for c in range(right, left - 1, -1):
                out.append(m[bottom][c])
            bottom -= 1
        if left <= right:  # a left column still exists
            for r in range(bottom, top - 1, -1):
                out.append(m[r][left])
            left += 1
    return out


def spiral_order_turning(m):
    """Same order, simulated: walk forward, turn right when blocked."""
    if not m or not m[0]:
        return []
    R, C = len(m), len(m[0])
    seen = [[False] * C for _ in range(R)]
    out, r, c, d = [], 0, 0, 0
    for _ in range(R * C):
        out.append(m[r][c])
        seen[r][c] = True
        nr, nc = r + DIRS4[d][0], c + DIRS4[d][1]
        if not (0 <= nr < R and 0 <= nc < C) or seen[nr][nc]:
            d = (d + 1) % 4
            nr, nc = r + DIRS4[d][0], c + DIRS4[d][1]
        r, c = nr, nc
    return out


def generate_matrix(n):
    """Spiral Matrix II: n x n filled with 1..n^2 in spiral order."""
    m = [[0] * n for _ in range(n)]
    top, bottom, left, right = 0, n - 1, 0, n - 1
    k = 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            m[top][c] = k
            k += 1
        top += 1
        for r in range(top, bottom + 1):
            m[r][right] = k
            k += 1
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                m[bottom][c] = k
                k += 1
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                m[r][left] = k
                k += 1
            left += 1
    return m


def spiral_matrix_iii(R, C, r0, c0):
    """Spiral Matrix III: cells of an R x C grid in the order a clockwise
    spiral from (r0, c0), starting east, visits them.
    """
    out = [[r0, c0]]
    r, c, d, length = r0, c0, 0, 1
    while len(out) < R * C:
        for _ in range(2):  # two sides per length
            dr, dc = DIRS4[d]
            for _ in range(length):
                r, c = r + dr, c + dc
                if 0 <= r < R and 0 <= c < C:
                    out.append([r, c])
            d = (d + 1) % 4
        length += 1
    return out


# ------------------------------------------------------------------------ tests


def spiral_iii_by_hugging(R, C, r0, c0):
    """Reference: walk an unbounded plane, turning right whenever the cell to
    the right is unvisited (the wall-hugging rule). No side lengths at all."""
    visited = {(r0, c0)}
    out = [[r0, c0]]
    r, c, d = r0, c0, 0
    while len(out) < R * C:
        r, c = r + DIRS4[d][0], c + DIRS4[d][1]
        visited.add((r, c))
        if 0 <= r < R and 0 <= c < C:
            out.append([r, c])
        rd = (d + 1) % 4
        if (r + DIRS4[rd][0], c + DIRS4[rd][1]) not in visited:
            d = rd
    return out


def random_shapes(rng, count=40, max_side=7):
    shapes = [(1, 1), (1, 6), (6, 1), (2, 5), (5, 2)]
    return shapes + [(rng.randint(1, max_side), rng.randint(1, max_side)) for _ in range(count)]


def test_known_examples():
    assert spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]
    assert spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
    assert spiral_order([]) == [] and spiral_order([[]]) == []


def test_boundaries_match_turning_simulation():
    rng = random.Random(10)
    for R, C in random_shapes(rng):
        m = [[rng.randint(0, 99) for _ in range(C)] for _ in range(R)]
        assert spiral_order(m) == spiral_order_turning(m), (R, C)


def test_thin_matrices_read_each_cell_once():
    assert spiral_order([[1, 2, 3, 4]]) == [1, 2, 3, 4]
    assert spiral_order([[1], [2], [3], [4]]) == [1, 2, 3, 4]
    assert spiral_order([[1, 2], [3, 4], [5, 6]]) == [1, 2, 4, 6, 5, 3]


def test_generate_is_inverse_of_spiral_order():
    for n in range(0, 9):
        m = generate_matrix(n)
        assert spiral_order(m) == list(range(1, n * n + 1))


def test_spiral_iii_matches_hugging_walk():
    rng = random.Random(11)
    for R, C in random_shapes(rng, 30):
        for _ in range(3):
            r0, c0 = rng.randrange(R), rng.randrange(C)
            got = spiral_matrix_iii(R, C, r0, c0)
            assert got == spiral_iii_by_hugging(R, C, r0, c0)
            assert sorted(map(tuple, got)) == [(r, c) for r in range(R) for c in range(C)]


def test_spiral_iii_example():
    assert spiral_matrix_iii(1, 4, 0, 0) == [[0, 0], [0, 1], [0, 2], [0, 3]]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
