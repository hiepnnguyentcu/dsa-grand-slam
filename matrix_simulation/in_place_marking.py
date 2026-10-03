"""In-place marking — store extra state inside the matrix itself.

Signs: "do it in place", "O(1) extra space", "all cells update at the same
       time" (Game of Life), "if a cell is 0 set its whole row and column to 0".
Approach: the trap is reading a cell you already overwrote. Two fixes:
  Marker row/column (Set Matrix Zeroes): use row 0 and column 0 as the flag
    arrays. Remember separately whether row 0 / column 0 had a zero, mark,
    zero the inner cells from the flags, then zero row 0 / column 0 last.
  Bit encoding (Game of Life): bit 0 = current state, bit 1 = next state.
    Neighbour counts read `& 1`, so pending updates never leak. A final pass
    shifts every cell right by one.
  Infinite board: keep only the live cells in a set; count neighbours with a
    Counter over the 8 offsets of each live cell.
Complexity: O(R C) time, O(1) extra (marker / bit tricks); O(live) sparse.
Gotchas:
  - Set zeroes: m[0][0] is shared by row 0 and column 0. Keep one separate
    flag for each, and zero row 0 / column 0 only after the inner pass.
  - Game of Life: every read during the counting pass must be `& 1`.
  - The bits work only while cell values are 0/1. For other values, encode
    with an unused sentinel (e.g. 2 = "alive -> dead", 3 = "dead -> alive").

Run the tests at the bottom with:  python3 matrix_simulation/in_place_marking.py
"""

import random
from collections import Counter


# ---------------------------------------------------------------- implementation


def set_zeroes(m):
    """Set Matrix Zeroes in place with O(1) extra space."""
    R, C = len(m), len(m[0])
    row0 = any(m[0][c] == 0 for c in range(C))
    col0 = any(m[r][0] == 0 for r in range(R))
    for r in range(1, R):
        for c in range(1, C):
            if m[r][c] == 0:
                m[r][0] = m[0][c] = 0  # flags live in the first row/column
    for r in range(1, R):
        for c in range(1, C):
            if m[r][0] == 0 or m[0][c] == 0:
                m[r][c] = 0
    if row0:
        for c in range(C):
            m[0][c] = 0
    if col0:
        for r in range(R):
            m[r][0] = 0


def set_zeroes_copy(m):
    """Reference: record zero rows and columns first, then build a new matrix."""
    rows = {r for r, row in enumerate(m) for x in row if x == 0}
    cols = {c for row in m for c, x in enumerate(row) if x == 0}
    return [[0 if r in rows or c in cols else x for c, x in enumerate(row)] for r, row in enumerate(m)]


DIRS8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def game_of_life(board):
    """Game of Life, one generation, in place via 2-bit encoding."""
    R, C = len(board), len(board[0])
    for r in range(R):
        for c in range(C):
            live = 0
            for dr, dc in DIRS8:
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C:
                    live += board[nr][nc] & 1  # current state only
            if live == 3 or (live == 2 and board[r][c] & 1):
                board[r][c] |= 2  # next state alive
    for r in range(R):
        for c in range(C):
            board[r][c] >>= 1


def game_of_life_copy(board):
    """Reference: read from the old board, write a fresh one."""
    R, C = len(board), len(board[0])
    out = [[0] * C for _ in range(R)]
    for r in range(R):
        for c in range(C):
            live = sum(board[r + dr][c + dc] for dr, dc in DIRS8
                       if 0 <= r + dr < R and 0 <= c + dc < C)
            out[r][c] = int(live == 3 or (live == 2 and board[r][c] == 1))
    return out


def game_of_life_sparse(live):
    """Unbounded board: set of live (r, c) -> next generation's set."""
    counts = Counter((r + dr, c + dc) for r, c in live for dr, dc in DIRS8)
    return {cell for cell, n in counts.items() if n == 3 or (n == 2 and cell in live)}


# ------------------------------------------------------------------------ tests


def random_shapes(rng, count=40, max_side=7):
    shapes = [(1, 1), (1, 6), (6, 1), (2, 5), (5, 2)]
    return shapes + [(rng.randint(1, max_side), rng.randint(1, max_side)) for _ in range(count)]


def test_set_zeroes_matches_copy():
    rng = random.Random(40)
    for R, C in random_shapes(rng, 120):
        m = [[rng.choice([0, 1, 2, 3, 4, 5, 6]) for _ in range(C)] for _ in range(R)]
        expected = set_zeroes_copy(m)
        set_zeroes(m)
        assert m == expected


def test_set_zeroes_corner_flags():
    # zero only in column 0 (not row 0): row 0 must keep its values
    m = [[1, 2, 3], [0, 5, 6], [7, 8, 9]]
    set_zeroes(m)
    assert m == [[0, 2, 3], [0, 0, 0], [0, 8, 9]]
    # zero only in row 0: column 0 below row 0 must keep its values
    m = [[1, 0, 3], [4, 5, 6]]
    set_zeroes(m)
    assert m == [[0, 0, 0], [4, 0, 6]]


def test_game_of_life_matches_copy_over_generations():
    rng = random.Random(41)
    for R, C in random_shapes(rng):
        b = [[rng.randint(0, 1) for _ in range(C)] for _ in range(R)]
        ref = [row[:] for row in b]
        for _ in range(5):
            game_of_life(b)
            ref = game_of_life_copy(ref)
            assert b == ref


def test_known_patterns():
    blinker = [[0, 0, 0], [1, 1, 1], [0, 0, 0]]
    game_of_life(blinker)
    assert blinker == [[0, 1, 0], [0, 1, 0], [0, 1, 0]]
    block = [[1, 1], [1, 1]]
    game_of_life(block)
    assert block == [[1, 1], [1, 1]]  # still life


def test_sparse_matches_dense_with_room_to_grow():
    rng = random.Random(42)
    gens = 4
    for _ in range(20):
        R, C = rng.randint(1, 6), rng.randint(1, 6)
        live = {(r, c) for r in range(R) for c in range(C) if rng.random() < 0.4}
        # dense board padded by one cell per generation never hits its edge
        P = gens
        dense = [[1 if (r - P, c - P) in live else 0 for c in range(C + 2 * P)] for r in range(R + 2 * P)]
        for _ in range(gens):
            live = game_of_life_sparse(live)
            game_of_life(dense)
        assert live == {(r - P, c - P) for r, row in enumerate(dense) for c, x in enumerate(row) if x}


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
