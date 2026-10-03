"""Gravity and compaction — things fall, slide, crush and merge.

Signs: "stones fall", "candies drop after crushing", "rotate the box",
       "2048 move", "tiles slide until blocked", repeat-until-stable boards.
Approach: compaction is read/write pointers on one line (see
  sliding_window/read_write.py for the 1D version).
    fall toward the end   -> write pointer starts at the end, read moves
                             backwards; a solid obstacle resets write to the
                             cell before it
    merge pass (2048)     -> compact non-zeros, merge equal neighbours once
                             left to right, pad with zeros
  Other directions: rotate so the move becomes "left" (or "down"), solve once,
  rotate back (rotate_flip.py).
  Candy Crush: mark every run of >= 3 (negate it so the value is still
  readable for overlapping runs), drop per column, repeat until no run.
Complexity: one compaction pass is O(R C). Candy Crush repeats up to
            O(R C) rounds in theory, O((R C)^2) total; tiny boards in practice.
Gotchas:
  - Mark all crushes first, then drop. Dropping while scanning breaks runs.
  - Compare with abs() while marking, or a cell in an L / T shape is missed.
  - 2048: a tile merges at most once per move ([2,2,2,2] -> [4,4,0,0], not
    [8,0,0,0]); merge from the side being moved toward.
  - Rotate the Box: set the old cell to '.' before writing '#', or a stone
    that does not move is erased.

Run the tests at the bottom with:  python3 matrix_simulation/gravity.py
"""

import random


# ---------------------------------------------------------------- implementation


def rotated_cw(m):
    return [list(row) for row in zip(*m[::-1])]


def rotate_the_box(box):
    """Rotating the Box: '#' stones fall right (until '*' or a stone), then the
    box turns 90 degrees clockwise so 'right' becomes 'down'."""
    box = [row[:] for row in box]
    for row in box:
        write = len(row) - 1
        for c in range(len(row) - 1, -1, -1):
            if row[c] == "*":
                write = c - 1
            elif row[c] == "#":
                row[c] = "."
                row[write] = "#"
                write -= 1
    return rotated_cw(box)


def candy_crush(board):
    """Candy Crush: crush runs of >= 3 equal positive values, drop, repeat.
    0 is empty. Mutates and returns board."""
    R, C = len(board), len(board[0])
    while True:
        crushed = False
        for r in range(R):
            for c in range(C - 2):
                v = abs(board[r][c])
                if v and v == abs(board[r][c + 1]) == abs(board[r][c + 2]):
                    board[r][c] = board[r][c + 1] = board[r][c + 2] = -v
                    crushed = True
        for r in range(R - 2):
            for c in range(C):
                v = abs(board[r][c])
                if v and v == abs(board[r + 1][c]) == abs(board[r + 2][c]):
                    board[r][c] = board[r + 1][c] = board[r + 2][c] = -v
                    crushed = True
        if not crushed:
            return board
        for c in range(C):  # gravity: keep positives, compacted to the bottom
            write = R - 1
            for r in range(R - 1, -1, -1):
                if board[r][c] > 0:
                    board[write][c] = board[r][c]
                    write -= 1
            for r in range(write, -1, -1):
                board[r][c] = 0


def slide_left(row):
    """One 2048 row moved left: compact, merge equal pairs once, pad."""
    tiles = [x for x in row if x]
    out, i = [], 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            out.append(tiles[i] * 2)
            i += 2
        else:
            out.append(tiles[i])
            i += 1
    return out + [0] * (len(row) - len(out))


TURNS = {"L": 0, "D": 1, "R": 2, "U": 3}  # clockwise turns that make the move "left"


def move_2048(board, direction):
    """Whole-board move in any direction via rotate -> slide left -> rotate back."""
    k = TURNS[direction]
    b = [row[:] for row in board]
    for _ in range(k):
        b = rotated_cw(b)
    b = [slide_left(row) for row in b]
    for _ in range((4 - k) % 4):
        b = rotated_cw(b)
    return b


# ------------------------------------------------------------------------ tests


def fall_right_by_ticks(box):
    """Reference: every tick, each stone with empty space to its right moves
    one cell. Stop when nothing moves."""
    box = [row[:] for row in box]
    moved = True
    while moved:
        moved = False
        for row in box:
            for c in range(len(row) - 2, -1, -1):
                if row[c] == "#" and row[c + 1] == ".":
                    row[c], row[c + 1] = ".", "#"
                    moved = True
    return box


def runs_to_crush(board):
    """Reference: cells in maximal horizontal/vertical runs of length >= 3."""
    R, C = len(board), len(board[0])
    cells = set()
    lines = [[(r, c) for c in range(C)] for r in range(R)] + [[(r, c) for r in range(R)] for c in range(C)]
    for line in lines:
        i = 0
        while i < len(line):
            j = i
            v = board[line[i][0]][line[i][1]]
            while j < len(line) and board[line[j][0]][line[j][1]] == v:
                j += 1
            if v and j - i >= 3:
                cells.update(line[i:j])
            i = j
    return cells


def candy_crush_reference(board):
    board = [row[:] for row in board]
    R, C = len(board), len(board[0])
    while True:
        cells = runs_to_crush(board)
        if not cells:
            return board
        for r, c in cells:
            board[r][c] = 0
        moved = True
        while moved:  # drop by ticks
            moved = False
            for r in range(R - 1):
                for c in range(C):
                    if board[r][c] and not board[r + 1][c]:
                        board[r][c], board[r + 1][c] = 0, board[r][c]
                        moved = True


def slide_left_by_steps(row):
    """Reference: the game's own loop. Push each tile left one cell at a time;
    merge into an equal neighbour that has not merged this move."""
    row = row[:]
    merged = [False] * len(row)
    for i in range(1, len(row)):
        if not row[i]:
            continue
        j = i
        while j > 0 and row[j - 1] == 0:
            row[j - 1], row[j] = row[j], 0
            j -= 1
        if j > 0 and row[j - 1] == row[j] and not merged[j - 1]:
            row[j - 1] *= 2
            row[j] = 0
            merged[j - 1] = True
    return row


def move_2048_direct(board, direction):
    """Reference: extract each line in move order, slide, write back. No rotation."""
    R, C = len(board), len(board[0])
    out = [row[:] for row in board]
    if direction in "LR":
        for r in range(R):
            line = board[r] if direction == "L" else board[r][::-1]
            res = slide_left_by_steps(line)
            out[r] = res if direction == "L" else res[::-1]
    else:
        for c in range(C):
            col = [board[r][c] for r in range(R)]
            line = col if direction == "U" else col[::-1]
            res = slide_left_by_steps(line)
            res = res if direction == "U" else res[::-1]
            for r in range(R):
                out[r][c] = res[r]
    return out


def random_shapes(rng, count=40, max_side=7):
    shapes = [(1, 1), (1, 6), (6, 1), (2, 5), (5, 2)]
    return shapes + [(rng.randint(1, max_side), rng.randint(1, max_side)) for _ in range(count)]


def test_rotate_the_box_matches_ticks():
    rng = random.Random(50)
    for R, C in random_shapes(rng, 80):
        box = [[rng.choice("#.*..") for _ in range(C)] for _ in range(R)]
        assert rotate_the_box(box) == rotated_cw(fall_right_by_ticks(box))


def test_rotate_the_box_example():
    assert rotate_the_box([["#", ".", "*", "."], ["#", "#", "*", "."]]) == [
        ["#", "."], ["#", "#"], ["*", "*"], [".", "."]]


def test_candy_crush_matches_reference():
    rng = random.Random(51)
    for R, C in random_shapes(rng, 150):
        b = [[rng.randint(1, 3) for _ in range(C)] for _ in range(R)]
        assert candy_crush([row[:] for row in b]) == candy_crush_reference(b)


def test_candy_crush_l_shape_crushed_together():
    b = [[1, 1, 1], [1, 2, 3], [1, 3, 2]]
    assert candy_crush(b) == [[0, 0, 0], [0, 2, 3], [0, 3, 2]]


def test_slide_left_matches_step_simulation():
    rng = random.Random(52)
    for _ in range(500):
        row = [rng.choice([0, 0, 2, 2, 4, 8]) for _ in range(rng.randint(1, 6))]
        assert slide_left(row) == slide_left_by_steps(row), row
    assert slide_left([2, 2, 2, 2]) == [4, 4, 0, 0]
    assert slide_left([4, 4, 8, 0]) == [8, 8, 0, 0]  # new 8 does not merge again


def test_rotation_trick_matches_direct_moves():
    rng = random.Random(53)
    for R, C in random_shapes(rng):
        b = [[rng.choice([0, 0, 2, 2, 4]) for _ in range(C)] for _ in range(R)]
        for d in "LRUD":
            assert move_2048(b, d) == move_2048_direct(b, d), (b, d)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
