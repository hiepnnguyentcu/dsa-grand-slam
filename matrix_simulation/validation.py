"""Validation and lookup — check rows, columns, boxes and diagonals in one pass.

Signs: "is this Sudoku board valid", "who won the tic-tac-toe game", "design
       tic-tac-toe with O(1) moves", "is this board reachable", "lucky
       numbers", "every row and column contains 1..n".
Approach: give every line a key and keep one set or counter per key.
    row r, column c                -> rows[r], cols[c]
    3 x 3 box                      -> boxes[(r // 3) * 3 + c // 3]
    diagonal / anti-diagonal       -> r == c, r + c == n - 1
  One scan updates every structure the cell belongs to; a duplicate (set) or
  a counter hitting +-n (tic-tac-toe, player A = +1, B = -1) is the answer.
Complexity: O(R C) per full check; O(1) per tic-tac-toe move with counters,
            versus O(n) to rescan the move's row/column/diagonals.
Gotchas:
  - Valid Sudoku checks only the filled cells for duplicates. It does not
    ask whether the board is solvable (that is backtracking/constraint_placement.py).
  - Box index is (r // 3) * 3 + c // 3. Forgetting the "* 3" maps nine boxes
    onto three.
  - Board reachability (Valid Tic-Tac-Toe): x_count is o_count or one more;
    X won -> X moved last; O won -> counts equal; both cannot win.
  - Lucky numbers: there is at most one (row min = col max is unique).

Run the tests at the bottom with:  python3 matrix_simulation/validation.py
"""

import itertools
import random


# ---------------------------------------------------------------- implementation


def is_valid_sudoku(board):
    """Valid Sudoku: no digit repeats in a row, column or 3x3 box ('.' is empty)."""
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v == ".":
                continue
            b = (r // 3) * 3 + c // 3
            if v in rows[r] or v in cols[c] or v in boxes[b]:
                return False
            rows[r].add(v)
            cols[c].add(v)
            boxes[b].add(v)
    return True


class TicTacToe:
    """Design Tic-Tac-Toe: n x n, O(1) per move, O(n) space.

    Player 1 adds +1, player 2 adds -1, to its row, column and (if on them)
    the two diagonals. A total of +-n means that line is all one player.
    """

    def __init__(self, n):
        self.n = n
        self.rows = [0] * n
        self.cols = [0] * n
        self.diag = 0
        self.anti = 0

    def move(self, r, c, player):
        """Returns the winner (1 or 2) after this move, else 0."""
        d = 1 if player == 1 else -1
        n = self.n
        self.rows[r] += d
        self.cols[c] += d
        if r == c:
            self.diag += d
        if r + c == n - 1:
            self.anti += d
        if n in (abs(self.rows[r]), abs(self.cols[c]), abs(self.diag), abs(self.anti)):
            return player
        return 0


def tictactoe_winner(moves):
    """Find Winner on a Tic Tac Toe Game: 'A', 'B', 'Draw' or 'Pending'."""
    game = TicTacToe(3)
    for i, (r, c) in enumerate(moves):
        if game.move(r, c, 1 if i % 2 == 0 else 2):
            return "A" if i % 2 == 0 else "B"
    return "Draw" if len(moves) == 9 else "Pending"


def _wins(board, p):
    lines = [[(r, c) for c in range(3)] for r in range(3)]
    lines += [[(r, c) for r in range(3)] for c in range(3)]
    lines += [[(i, i) for i in range(3)], [(i, 2 - i) for i in range(3)]]
    return any(all(board[r][c] == p for r, c in line) for line in lines)


def valid_tic_tac_toe(board):
    """Valid Tic-Tac-Toe State: could this board arise in a real game?"""
    x = sum(row.count("X") for row in board)
    o = sum(row.count("O") for row in board)
    if o not in (x, x - 1):
        return False
    x_win, o_win = _wins(board, "X"), _wins(board, "O")
    if x_win and o_win:
        return False
    if x_win and x != o + 1:
        return False
    if o_win and x != o:
        return False
    return True


def lucky_numbers(m):
    """Lucky Numbers in a Matrix: minimum of its row and maximum of its column."""
    row_mins = {min(row) for row in m}
    col_maxes = {max(col) for col in zip(*m)}
    return sorted(row_mins & col_maxes)


def check_valid(m):
    """Check if Every Row and Column Contains All Numbers 1..n."""
    want = set(range(1, len(m) + 1))
    return all(set(row) == want for row in m) and all(set(col) == want for col in zip(*m))


# ------------------------------------------------------------------------ tests


def sudoku_units():
    units = [[(r, c) for c in range(9)] for r in range(9)]
    units += [[(r, c) for r in range(9)] for c in range(9)]
    units += [[(br + i, bc + j) for i in range(3) for j in range(3)]
              for br in (0, 3, 6) for bc in (0, 3, 6)]
    return units


def sudoku_brute(board):
    for unit in sudoku_units():
        vals = [board[r][c] for r, c in unit if board[r][c] != "."]
        if len(vals) != len(set(vals)):
            return False
    return True


SOLVED = [[str((r * 3 + r // 3 + c) % 9 + 1) for c in range(9)] for r in range(9)]


def test_sudoku_matches_unit_brute_force():
    rng = random.Random(60)
    assert sudoku_brute(SOLVED)
    for _ in range(400):
        b = [[v if rng.random() < 0.35 else "." for v in row] for row in SOLVED]
        if rng.random() < 0.6:  # inject a random digit, often a clash
            b[rng.randrange(9)][rng.randrange(9)] = str(rng.randint(1, 9))
        assert is_valid_sudoku(b) == sudoku_brute(b)


def test_sudoku_box_clash_only():
    b = [["."] * 9 for _ in range(9)]
    b[0][0] = b[1][1] = "5"  # different row and column, same box
    assert not is_valid_sudoku(b)
    b[1][1] = "."
    b[4][4] = "5"            # different box
    assert is_valid_sudoku(b)


def test_counters_match_board_rescan():
    rng = random.Random(61)
    for n in range(1, 6):
        for _ in range(30):
            game = TicTacToe(n)
            board = [[0] * n for _ in range(n)]
            cells = [(r, c) for r in range(n) for c in range(n)]
            rng.shuffle(cells)
            for i, (r, c) in enumerate(cells):
                p = 1 + i % 2
                board[r][c] = p
                lines = [board[r], [board[k][c] for k in range(n)]]
                if r == c:
                    lines.append([board[k][k] for k in range(n)])
                if r + c == n - 1:
                    lines.append([board[k][n - 1 - k] for k in range(n)])
                expected = p if any(all(x == p for x in line) for line in lines) else 0
                assert game.move(r, c, p) == expected
                if expected:
                    break


def test_winner_matches_board_check():
    rng = random.Random(62)
    for _ in range(300):
        cells = [(r, c) for r in range(3) for c in range(3)]
        rng.shuffle(cells)
        board = [["."] * 3 for _ in range(3)]
        moves = []
        for i, (r, c) in enumerate(cells):
            board[r][c] = "X" if i % 2 == 0 else "O"
            moves.append([r, c])
            if _wins(board, "X") or _wins(board, "O"):
                break
        k = rng.randint(0, len(moves))  # any prefix of a legal game
        pre = [["."] * 3 for _ in range(3)]
        for i, (r, c) in enumerate(moves[:k]):
            pre[r][c] = "X" if i % 2 == 0 else "O"
        expected = "A" if _wins(pre, "X") else "B" if _wins(pre, "O") else ("Draw" if k == 9 else "Pending")
        assert tictactoe_winner(moves[:k]) == expected


def test_valid_state_matches_reachable_set():
    # every board reachable by real play, found by exploring the game tree
    start = ("." * 9,)
    reachable, frontier = set(start), list(start)
    while frontier:
        s = frontier.pop()
        b = [s[0:3], s[3:6], s[6:9]]
        if _wins(b, "X") or _wins(b, "O"):
            continue  # game over, no further moves
        p = "X" if s.count("X") == s.count("O") else "O"
        for i, ch in enumerate(s):
            if ch == ".":
                t = s[:i] + p + s[i + 1:]
                if t not in reachable:
                    reachable.add(t)
                    frontier.append(t)
    for cells in itertools.product("XO.", repeat=9):
        s = "".join(cells)
        assert valid_tic_tac_toe([s[0:3], s[3:6], s[6:9]]) == (s in reachable), s


def test_lucky_numbers_brute():
    rng = random.Random(63)
    for _ in range(200):
        R, C = rng.randint(1, 5), rng.randint(1, 5)
        vals = rng.sample(range(100), R * C)  # distinct, as the problem states
        m = [vals[r * C:(r + 1) * C] for r in range(R)]
        brute = [m[r][c] for r in range(R) for c in range(C)
                 if m[r][c] == min(m[r]) and m[r][c] == max(m[k][c] for k in range(R))]
        assert lucky_numbers(m) == sorted(brute)
        assert len(brute) <= 1


def test_check_valid():
    rng = random.Random(64)
    for n in range(1, 6):
        latin = [[(r + c) % n + 1 for c in range(n)] for r in range(n)]
        assert check_valid(latin)
        if n > 1:
            bad = [row[:] for row in latin]
            r, c = rng.randrange(n), rng.randrange(n)
            bad[r][c] = bad[r][c] % n + 1  # a duplicate in row r
            assert not check_valid(bad)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
