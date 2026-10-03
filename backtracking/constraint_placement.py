"""Constraint placement — N-Queens and Sudoku.

Signs: place items on a board so no two conflict; fill blanks so every row,
       column and box obeys a rule; "return all boards" or "solve in place".
Approach: one decision per level (row for queens, empty cell for Sudoku).
          Keep the constraints as sets or bitmasks so "is this legal?" is O(1)
          instead of rescanning the board.
            - N-Queens: one queen per row, so recurse by row. A column, a
              "/" diagonal (r + c) and a "\" diagonal (r - c) may each hold
              one queen.
            - Bitmask N-Queens (count only): cols / d1 / d2 as ints; free
              positions = ~(cols | d1 | d2) & full; shift the diagonals by
              one each row. `free & -free` peels the lowest free bit.
            - Sudoku: rows / cols / boxes as 9-bit masks. Pick the empty cell
              with the *fewest* candidates (MRV) — it fails fastest and makes
              hard puzzles solve in milliseconds. Return True to stop at the
              first solution; undo on the way back otherwise.
Complexity: N-Queens about O(n!) with pruning; Sudoku worst case 9^(empty)
            but MRV makes real puzzles near-instant.
Gotchas:
  - Diagonal ids: r - c ranges -(n-1)..n-1; offset by n-1 for a list, or use
    a set.
  - Sudoku box index is (r // 3) * 3 + c // 3.
  - Sudoku must return a success flag up the stack, or the unchoose step
    erases the solution as the recursion unwinds.
  - Bitmask shift direction: d1 moves left, d2 moves right, both masked to n
    bits.

Run the tests at the bottom with:  python3 backtracking/constraint_placement.py
"""

import random
from itertools import permutations


# ---------------------------------------------------------------- implementation


def solve_n_queens(n):
    """All boards as lists of strings, queens as 'Q'."""
    out, cols, d1, d2, queen_col = [], set(), set(), set(), []

    def go(r):
        if r == n:
            out.append(["." * c + "Q" + "." * (n - c - 1) for c in queen_col])
            return
        for c in range(n):
            if c in cols or r + c in d1 or r - c in d2:
                continue
            cols.add(c); d1.add(r + c); d2.add(r - c); queen_col.append(c)
            go(r + 1)
            cols.discard(c); d1.discard(r + c); d2.discard(r - c); queen_col.pop()
    go(0)
    return out


def total_n_queens(n):
    """Count only, with bitmasks. No undo needed: masks are passed by value."""
    full = (1 << n) - 1

    def go(cols, d1, d2):
        if cols == full:
            return 1
        count, free = 0, ~(cols | d1 | d2) & full
        while free:
            bit = free & -free                # lowest free column
            free ^= bit
            count += go(cols | bit, (d1 | bit) << 1 & full, (d2 | bit) >> 1)
        return count
    return go(0, 0, 0)


def solve_sudoku(board):
    """Fill a 9x9 board of digits (0 = empty) in place. Returns True if solved."""
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    empty = []
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v:
                bit = 1 << v
                if rows[r] & bit or cols[c] & bit or boxes[r // 3 * 3 + c // 3] & bit:
                    return False              # givens already conflict
                rows[r] |= bit; cols[c] |= bit; boxes[r // 3 * 3 + c // 3] |= bit
            else:
                empty.append((r, c))

    def candidates(r, c):
        used = rows[r] | cols[c] | boxes[r // 3 * 3 + c // 3]
        return [v for v in range(1, 10) if not used >> v & 1]

    def go():
        if not empty:
            return True
        # MRV: branch on the most constrained cell.
        k = min(range(len(empty)), key=lambda i: len(candidates(*empty[i])))
        empty[k], empty[-1] = empty[-1], empty[k]
        r, c = empty.pop()
        b = r // 3 * 3 + c // 3
        for v in candidates(r, c):
            bit = 1 << v
            board[r][c] = v; rows[r] |= bit; cols[c] |= bit; boxes[b] |= bit
            if go():
                return True                   # keep the filled board
            board[r][c] = 0; rows[r] ^= bit; cols[c] ^= bit; boxes[b] ^= bit
        empty.append((r, c))
        return False
    return go()


# ------------------------------------------------------------------------ tests


def brute_force_queens(n):
    """Every permutation is one queen per row and column; keep diagonal-safe ones."""
    return [p for p in permutations(range(n))
            if len({r + c for r, c in enumerate(p)}) == n
            and len({r - c for r, c in enumerate(p)}) == n]


def valid_solution(board, givens):
    full = set(range(1, 10))
    for i in range(9):
        if set(board[i]) != full or {board[r][i] for r in range(9)} != full:
            return False
        br, bc = i // 3 * 3, i % 3 * 3
        if {board[br + a][bc + b] for a in range(3) for b in range(3)} != full:
            return False
    return all(givens[r][c] in (0, board[r][c]) for r in range(9) for c in range(9))


def test_n_queens_vs_brute_force():
    for n in range(1, 8):
        boards = solve_n_queens(n)
        as_perms = sorted(tuple(row.index("Q") for row in b) for b in boards)
        assert as_perms == sorted(brute_force_queens(n))
        assert total_n_queens(n) == len(boards)


def test_n_queens_known_counts():
    known = [1, 1, 0, 0, 2, 10, 4, 40, 92, 352]
    for n, want in enumerate(known):
        if n == 0:
            continue
        assert total_n_queens(n) == want
    assert solve_n_queens(4) == [[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]]


def test_sudoku_classic():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    givens = [row[:] for row in puzzle]
    assert solve_sudoku(puzzle)
    assert valid_solution(puzzle, givens)
    assert puzzle[0] == [5, 3, 4, 6, 7, 8, 9, 1, 2]


def test_sudoku_random_puzzles():
    # Build a solved grid from the standard pattern, shuffle digits, blank cells.
    random.seed(12)
    base = [[(3 * (r % 3) + r // 3 + c) % 9 + 1 for c in range(9)] for r in range(9)]
    for _ in range(8):
        perm = list(range(1, 10)); random.shuffle(perm)
        solved = [[perm[v - 1] for v in row] for row in base]
        puzzle = [[v if random.random() < 0.35 else 0 for v in row] for row in solved]
        givens = [row[:] for row in puzzle]
        assert solve_sudoku(puzzle)
        assert valid_solution(puzzle, givens)


def test_sudoku_unsolvable():
    bad = [[0] * 9 for _ in range(9)]
    bad[0][0] = bad[0][1] = 5                  # conflicting givens
    assert solve_sudoku(bad) is False
    # Legal givens, but cell (0, 8) has no candidate left.
    stuck = [[0] * 9 for _ in range(9)]
    stuck[0][:8] = [1, 2, 3, 4, 5, 6, 7, 8]
    stuck[1][8] = 9
    assert solve_sudoku(stuck) is False


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
