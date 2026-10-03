"""2D grid idioms — direction arrays, bounds, flattening, sentinel padding.

Signs: any problem on an R x C grid: "neighbours of a cell", "reshape",
       "shift the grid k times", "average of the 3x3 block around each cell",
       "turn left / right", a 1D index that must become (r, c) or back.
Approach: a handful of reusable one-liners.
    DIRS4 clockwise from east  -> turn right = (d + 1) % 4, left = (d + 3) % 4
    in bounds                  -> 0 <= r < R and 0 <= c < C
    flatten / unflatten        -> i = r * C + c,  (r, c) = divmod(i, C)
    sentinel padding           -> wrap the grid in a border so edge cells need
                                  no bounds checks
  Reshape and shift are flatten -> new index -> unflatten; no data moves twice.
Complexity: O(1) per index conversion; O(R C) per full-grid pass.
Gotchas:
  - divmod by C (the column count), not R. Flatten uses C too.
  - Python's -1 index wraps silently: grid[-1][c] is the last row, not an
    error. Always bounds-check before indexing a neighbour.
  - Pick one direction order and stick to it. DIRS4 here is clockwise, so
    index arithmetic turns the robot.
  - BFS/DFS over grid neighbours lives in graphs/ (bfs.py, dfs.py,
    modeling.grid_neighbors). This file is the indexing layer under those.

Run the tests at the bottom with:  python3 matrix_simulation/grid_idioms.py
"""

import random


# ---------------------------------------------------------------- implementation

DIRS4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # E, S, W, N — clockwise
DIRS8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def in_bounds(r, c, R, C):
    return 0 <= r < R and 0 <= c < C


def turn_right(d):
    return (d + 1) % 4


def turn_left(d):
    return (d + 3) % 4  # never (d - 1) % 4 in languages where % can be negative


def flatten(r, c, C):
    return r * C + c


def unflatten(i, C):
    return divmod(i, C)


def matrix_reshape(mat, r, c):
    """Reshape Matrix: same row-major order, new shape; original if impossible."""
    R, C = len(mat), len(mat[0])
    if R * C != r * c:
        return mat
    out = [[0] * c for _ in range(r)]
    for i in range(R * C):
        out[i // c][i % c] = mat[i // C][i % C]
    return out


def construct_2d(original, m, n):
    """Convert 1D Array Into 2D Array: slice rows of length n; [] if impossible."""
    if len(original) != m * n:
        return []
    return [original[i * n:(i + 1) * n] for i in range(m)]


def shift_grid(grid, k):
    """Shift 2D Grid k times: each element moves one step right, wrapping to the
    next row, and the last element wraps to (0, 0).

    That is a rotation of the flattened array: index i goes to (i + k) % (R C).
    """
    R, C = len(grid), len(grid[0])
    total = R * C
    out = [[0] * C for _ in range(R)]
    for i in range(total):
        j = (i + k) % total
        out[j // C][j % C] = grid[i // C][i % C]
    return out


def image_smoother(img):
    """Image Smoother: floor of the mean of each cell and its in-bounds 8 neighbours."""
    R, C = len(img), len(img[0])
    out = [[0] * C for _ in range(R)]
    for r in range(R):
        for c in range(C):
            total, count = img[r][c], 1
            for dr, dc in DIRS8:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc, R, C):
                    total += img[nr][nc]
                    count += 1
            out[r][c] = total // count
    return out


def pad(grid, fill):
    """Grid wrapped in a one-cell border of `fill`. Cell (r, c) moves to (r+1, c+1)."""
    C = len(grid[0])
    border = [fill] * (C + 2)
    return [border[:]] + [[fill] + row[:] + [fill] for row in grid] + [border[:]]


def image_smoother_padded(img):
    """Same answer via padding: sum and count over a padded grid, no bounds checks.

    The count grid is padded with 0 and filled with 1, so it counts real cells.
    """
    R, C = len(img), len(img[0])
    vals = pad(img, 0)
    ones = pad([[1] * C for _ in range(R)], 0)
    out = [[0] * C for _ in range(R)]
    for r in range(1, R + 1):
        for c in range(1, C + 1):
            s = sum(vals[r + dr][c + dc] for dr in (-1, 0, 1) for dc in (-1, 0, 1))
            n = sum(ones[r + dr][c + dc] for dr in (-1, 0, 1) for dc in (-1, 0, 1))
            out[r - 1][c - 1] = s // n
    return out


# ------------------------------------------------------------------------ tests


def random_grid(rng, R, C, lo=0, hi=9):
    return [[rng.randint(lo, hi) for _ in range(C)] for _ in range(R)]


def random_shapes(rng, count=40, max_side=6):
    """Random (R, C) pairs, always including the thin 1 x n and n x 1 cases."""
    shapes = [(1, 1), (1, 5), (5, 1), (1, max_side), (max_side, 1)]
    shapes += [(rng.randint(1, max_side), rng.randint(1, max_side)) for _ in range(count)]
    return shapes


def test_turns_cycle_back():
    for d in range(4):
        assert turn_left(turn_right(d)) == d
        assert turn_right(turn_right(turn_right(turn_right(d)))) == d
    # turning right from east faces south: dr becomes +1
    assert DIRS4[turn_right(0)] == (1, 0)


def test_flatten_round_trip():
    R, C = 4, 7
    seen = set()
    for r in range(R):
        for c in range(C):
            i = flatten(r, c, C)
            assert unflatten(i, C) == (r, c)
            seen.add(i)
    assert seen == set(range(R * C))  # a bijection onto 0..RC-1


def test_reshape_matches_flat_list():
    rng = random.Random(1)
    for R, C in random_shapes(rng):
        g = random_grid(rng, R, C)
        flat = [x for row in g for x in row]
        for r in range(1, R * C + 1):
            if (R * C) % r == 0:
                c = R * C // r
                out = matrix_reshape(g, r, c)
                assert out == construct_2d(flat, r, c)
                assert [x for row in out for x in row] == flat
        assert matrix_reshape(g, R * C + 1, 1) is g  # impossible shape


def test_construct_2d_rejects_bad_size():
    assert construct_2d([1, 2, 3], 2, 2) == []
    assert construct_2d([1, 2, 3, 4], 2, 2) == [[1, 2], [3, 4]]


def test_shift_grid_matches_step_by_step():
    def one_step(g):
        R, C = len(g), len(g[0])
        out = [[0] * C for _ in range(R)]
        for r in range(R):
            for c in range(C):
                if c + 1 < C:
                    out[r][c + 1] = g[r][c]
                elif r + 1 < R:
                    out[r + 1][0] = g[r][c]
                else:
                    out[0][0] = g[r][c]
        return out

    rng = random.Random(2)
    for R, C in random_shapes(rng, 25):
        g = random_grid(rng, R, C)
        cur = g
        for k in range(R * C + 3):
            assert shift_grid(g, k) == cur
            cur = one_step(cur)


def test_image_smoother_two_ways():
    rng = random.Random(3)
    for R, C in random_shapes(rng):
        g = random_grid(rng, R, C, 0, 255)
        assert image_smoother(g) == image_smoother_padded(g)
    assert image_smoother([[1, 1, 1], [1, 0, 1], [1, 1, 1]]) == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]


def test_pad_shape_and_offset():
    g = [[1, 2, 3], [4, 5, 6]]
    p = pad(g, 0)
    assert len(p) == 4 and all(len(row) == 5 for row in p)
    assert p[1 + 1][2 + 1] == g[1][2]
    assert sum(map(sum, p)) == sum(map(sum, g))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
