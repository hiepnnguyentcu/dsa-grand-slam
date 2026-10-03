"""Rotate, flip, transpose — in-place and copy-based matrix transforms.

Signs: "rotate the image 90 degrees in place", "flip horizontally", "transpose",
       "can mat become target by rotations", "rotate k quarter turns",
       anything that is "the same move, in a different direction".
Approach: every 90-degree turn is two reflections.
    clockwise          = transpose, then reverse each row
    counter-clockwise  = transpose, then reverse the row order
    180                = reverse rows and reverse each row
  4-way cycle (alternative): for each layer and offset, rotate the four
  matching cells in one swap: top <- left <- bottom <- right <- top.
  Non-square: no in-place rotation; build a copy.
    clockwise copy     = zip(*m[::-1])        new[c][R-1-r] = m[r][c]
    counter-clockwise  = zip(*m)[::-1]        new[C-1-c][r] = m[r][c]
Complexity: O(n^2) time, O(1) extra for the square in-place versions;
            O(R C) for copies.
Gotchas:
  - In-place transpose swaps only above the diagonal (c > r). Looping all
    cells swaps every pair twice and changes nothing.
  - zip returns tuples; convert rows back to lists before mutating.
  - Rotating a non-square matrix swaps its shape: R x C becomes C x R.
  - k quarter turns: reduce k % 4 first (and k % 4 handles negatives in Python).
  - "Move in direction X" problems (2048, gravity): rotate so X becomes
    "left", solve once, rotate back. See gravity.py.

Run the tests at the bottom with:  python3 matrix_simulation/rotate_flip.py
"""

import random


# ---------------------------------------------------------------- implementation


def transpose(m):
    """Any shape: R x C -> C x R copy."""
    return [list(col) for col in zip(*m)]


def transpose_in_place(m):
    """Square only: swap across the main diagonal."""
    n = len(m)
    for r in range(n):
        for c in range(r + 1, n):
            m[r][c], m[c][r] = m[c][r], m[r][c]


def rotate_cw(m):
    """Rotate Image: 90 degrees clockwise in place (square)."""
    transpose_in_place(m)
    for row in m:
        row.reverse()


def rotate_ccw(m):
    """90 degrees counter-clockwise in place (square)."""
    transpose_in_place(m)
    m.reverse()


def rotate_cw_cycle(m):
    """Rotate Image via 4-way swaps, layer by layer, one temp variable."""
    n = len(m)
    for layer in range(n // 2):
        first, last = layer, n - 1 - layer
        for i in range(first, last):
            off = i - first
            top = m[first][i]
            m[first][i] = m[last - off][first]       # left   -> top
            m[last - off][first] = m[last][last - off]  # bottom -> left
            m[last][last - off] = m[i][last]         # right  -> bottom
            m[i][last] = top                         # top    -> right


def rotated_cw(m):
    """Any shape, copy: clockwise."""
    return [list(row) for row in zip(*m[::-1])]


def rotated_ccw(m):
    """Any shape, copy: counter-clockwise."""
    return [list(row) for row in zip(*m)][::-1]


def rotated_k(m, k):
    """k clockwise quarter turns (negative k turns counter-clockwise)."""
    for _ in range(k % 4):
        m = rotated_cw(m)
    return [row[:] for row in m]


def flip_horizontal(m):
    """Mirror left-right in place."""
    for row in m:
        row.reverse()


def flip_vertical(m):
    """Mirror top-bottom in place."""
    m.reverse()


def flip_and_invert(image):
    """Flipping an Image: mirror each row and invert bits, one pass with two
    pointers. When both ends are equal they flip to the same new value."""
    for row in image:
        i, j = 0, len(row) - 1
        while i <= j:
            row[i], row[j] = row[j] ^ 1, row[i] ^ 1
            i += 1
            j -= 1
    return image


def find_rotation(mat, target):
    """Determine Whether Matrix Can Be Obtained By Rotation."""
    for _ in range(4):
        if mat == target:
            return True
        mat = rotated_cw(mat)
    return False


# ------------------------------------------------------------------------ tests


def random_matrix(rng, R, C):
    return [[rng.randint(0, 99) for _ in range(C)] for _ in range(R)]


def random_shapes(rng, count=40, max_side=7):
    shapes = [(1, 1), (1, 6), (6, 1), (2, 5), (5, 2)]
    return shapes + [(rng.randint(1, max_side), rng.randint(1, max_side)) for _ in range(count)]


def cw_by_formula(m):
    R, C = len(m), len(m[0])
    out = [[None] * R for _ in range(C)]
    for r in range(R):
        for c in range(C):
            out[c][R - 1 - r] = m[r][c]
    return out


def ccw_by_formula(m):
    R, C = len(m), len(m[0])
    out = [[None] * R for _ in range(C)]
    for r in range(R):
        for c in range(C):
            out[C - 1 - c][r] = m[r][c]
    return out


def test_copies_match_index_formulas_any_shape():
    rng = random.Random(30)
    for R, C in random_shapes(rng):
        m = random_matrix(rng, R, C)
        assert rotated_cw(m) == cw_by_formula(m)
        assert rotated_ccw(m) == ccw_by_formula(m)
        assert transpose(m) == [[m[r][c] for r in range(R)] for c in range(C)]


def test_in_place_versions_agree_with_copies():
    rng = random.Random(31)
    for n in range(1, 9):
        for _ in range(5):
            m = random_matrix(rng, n, n)
            a, b, c = [r[:] for r in m], [r[:] for r in m], [r[:] for r in m]
            rotate_cw(a)
            rotate_cw_cycle(b)
            rotate_ccw(c)
            assert a == b == rotated_cw(m)
            assert c == rotated_ccw(m)


def test_four_turns_is_identity_and_k_reduces():
    rng = random.Random(32)
    for R, C in random_shapes(rng, 20):
        m = random_matrix(rng, R, C)
        assert rotated_k(m, 4) == m
        assert rotated_k(m, 0) == m
        assert rotated_k(m, -1) == rotated_ccw(m)
        assert rotated_k(m, 6) == rotated_cw(rotated_cw(m))
        assert rotated_ccw(rotated_cw(m)) == m


def test_rotation_is_two_reflections():
    rng = random.Random(33)
    for n in range(1, 8):
        m = random_matrix(rng, n, n)
        a = [r[:] for r in m]
        flip_vertical(a)          # reverse rows, then transpose = clockwise
        assert transpose(a) == rotated_cw(m)
        b = [r[:] for r in m]
        flip_horizontal(b)
        flip_vertical(b)
        assert b == rotated_k(m, 2)


def test_flip_and_invert_matches_naive():
    rng = random.Random(34)
    for R, C in random_shapes(rng):
        img = [[rng.randint(0, 1) for _ in range(C)] for _ in range(R)]
        expected = [[1 - x for x in row[::-1]] for row in img]
        assert flip_and_invert([r[:] for r in img]) == expected


def test_find_rotation():
    rng = random.Random(35)
    for n in range(1, 6):
        m = [[rng.randint(0, 1) for _ in range(n)] for _ in range(n)]
        for k in range(4):
            assert find_rotation(m, rotated_k(m, k))
    assert not find_rotation([[0, 1], [1, 1]], [[1, 0], [0, 1]])


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
