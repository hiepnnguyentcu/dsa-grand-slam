"""Grid / path search — word search, N-Queens, Sudoku, maze paths, gold.

Signs: a board or graph, "find a path that spells / visits / collects",
       "place so no two attack", "fill the board".
Approach: dfs(r, c) is the slot. Mark the cell (board[r][c] = '#' or a
          visited set), try 4 directions, unmark. Placement puzzles use
          lookup sets (cols, diagonals, row/col/box) as the state to undo.
          Return bool when one answer is enough: `if dfs(...): return True`.
Complexity: word search O(R*C * 3^L); N-Queens O(n!); unique paths III
            O(3^(R*C)).
Gotchas:
  - Unmark on EVERY exit path, including the early `return True` if the
    board must be restored (79 doesn't care, 212 does).
  - N-Queens diagonals: r + c is one, r - c the other.
  - Sudoku: unchoose in reverse order of choose; return True keeps the board.
  - 212: build a trie, pop the word when found, prune empty trie nodes.
  - Flood fill (733, 200) needs no unmark — a cell is done once visited.
  - Euler / itinerary (332) is Hierholzer: graphs/euler_path.py.

Run the tests at the bottom with:  python3 backtracking/grid_search.py
"""

import random
from itertools import permutations, product


DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


# ---------------------------------------------------------------- implementation


def exist(board, word):
    """LC 79."""
    rows, cols = len(board), len(board[0])

    def dfs(r, c, start):
        if start == len(word):
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[start]:
            return False
        char = board[r][c]
        board[r][c] = "#"
        for dr, dc in DIRECTIONS:
            if dfs(r + dr, c + dc, start + 1):
                board[r][c] = char
                return True
        board[r][c] = char
        return False

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False


def find_words(board, words):
    """LC 212. Trie of words; walk board and trie together."""
    trie = {}
    for word in words:
        node = trie
        for char in word:
            node = node.setdefault(char, {})
        node["$"] = word

    rows, cols = len(board), len(board[0])
    res = []

    def dfs(r, c, parent):
        char = board[r][c]
        node = parent.get(char)
        if node is None:
            return
        if "$" in node:
            res.append(node.pop("$"))          # report once
        board[r][c] = "#"
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                dfs(nr, nc, node)
        board[r][c] = char
        if not node:
            parent.pop(char)                   # prune exhausted branch

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie)
    return res


def solve_n_queens(n):
    """LC 51. Row = slot, column = choice."""
    res = []
    col_set, diag_set, anti_set = set(), set(), set()
    board = [["." for _ in range(n)] for _ in range(n)]

    def dfs(r):
        if r == n:
            res.append(["".join(row) for row in board])
            return
        for c in range(n):
            if c in col_set or r - c in diag_set or r + c in anti_set:
                continue
            col_set.add(c); diag_set.add(r - c); anti_set.add(r + c)
            board[r][c] = "Q"
            dfs(r + 1)
            board[r][c] = "."
            col_set.remove(c); diag_set.remove(r - c); anti_set.remove(r + c)
    dfs(0)
    return res


def total_n_queens(n):
    """LC 52. Same tree, count instead of record."""
    col_set, diag_set, anti_set = set(), set(), set()

    def dfs(r):
        if r == n:
            return 1
        count = 0
        for c in range(n):
            if c in col_set or r - c in diag_set or r + c in anti_set:
                continue
            col_set.add(c); diag_set.add(r - c); anti_set.add(r + c)
            count += dfs(r + 1)
            col_set.remove(c); diag_set.remove(r - c); anti_set.remove(r + c)
        return count
    return dfs(0)


def solve_sudoku(board):
    """LC 37. Fill board ('.' = empty) in place."""
    row_sets = [set() for _ in range(9)]
    col_sets = [set() for _ in range(9)]
    box_sets = [[set() for _ in range(3)] for _ in range(3)]

    # Pre-populate our lookups
    for r in range(9):
        for c in range(9):
            char = board[r][c]
            if char != ".":
                row_sets[r].add(char)
                col_sets[c].add(char)
                box_sets[r // 3][c // 3].add(char)

    def dfs(r, c):
        # Base case: if we reach row 9, we successfully filled the whole board
        if r == 9:
            return True
        # If we reach the end of a column, move to the start of the next row
        if c == 9:
            return dfs(r + 1, 0)

        # If the cell is already filled, skip to the next cell immediately
        if board[r][c] != ".":
            return dfs(r, c + 1)

        # Try placing digits 1-9
        for i in range(1, 10):
            digit = str(i)
            if digit in row_sets[r] or digit in col_sets[c] or digit in box_sets[r // 3][c // 3]:
                continue

            # Choose
            row_sets[r].add(digit)
            col_sets[c].add(digit)
            box_sets[r // 3][c // 3].add(digit)
            board[r][c] = digit

            # Explore next cell
            if dfs(r, c + 1):
                return True

            # Unchoose (Backtrack)
            board[r][c] = "."
            box_sets[r // 3][c // 3].remove(digit)
            col_sets[c].remove(digit)
            row_sets[r].remove(digit)

        return False

    dfs(0, 0)


def unique_paths_with_obstacles(grid):
    """LC 63. Count right/down paths. Monotone moves -> no visited needed."""
    rows, cols = len(grid), len(grid[0])

    def dfs(r, c):
        if r >= rows or c >= cols or grid[r][c] == 1:
            return 0
        if r == rows - 1 and c == cols - 1:
            return 1
        return dfs(r + 1, c) + dfs(r, c + 1)
    return dfs(0, 0)


def rat_in_maze(grid):
    """All 4-direction paths (0,0) -> (n-1,n-1) over open cells (1), as 'DLRU' strings."""
    n = len(grid)
    moves = [(1, 0, "D"), (0, -1, "L"), (0, 1, "R"), (-1, 0, "U")]
    visited = [[False for _ in range(n)] for _ in range(n)]
    res = []

    def dfs(r, c, res, temp):
        if r == n - 1 and c == n - 1:
            res.append("".join(temp))
            return
        for dr, dc, move in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 1 and not visited[nr][nc]:
                visited[nr][nc] = True
                temp.append(move)
                dfs(nr, nc, res, temp)
                temp.pop()
                visited[nr][nc] = False

    if grid[0][0] == 1 and grid[n - 1][n - 1] == 1:
        visited[0][0] = True
        dfs(0, 0, res, [])
    return res


def unique_paths_iii(grid):
    """LC 980. 1 = start, 2 = end, -1 = wall; walk every non-wall cell once."""
    rows, cols = len(grid), len(grid[0])
    empty = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != -1:
                empty += 1
            if grid[r][c] == 1:
                sr, sc = r, c

    def dfs(r, c, left):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == -1:
            return 0
        if grid[r][c] == 2:
            return 1 if left == 1 else 0
        temp = grid[r][c]
        grid[r][c] = -1
        count = 0
        for dr, dc in DIRECTIONS:
            count += dfs(r + dr, c + dc, left - 1)
        grid[r][c] = temp
        return count
    return dfs(sr, sc, empty)


def all_paths_source_target(graph):
    """LC 797. DAG -> no visited needed."""
    n = len(graph)
    res = []

    def dfs(node, res, temp):
        if node == n - 1:
            res.append(temp.copy())
            return
        for nei in graph[node]:
            temp.append(nei)
            dfs(nei, res, temp)
            temp.pop()
    dfs(0, res, [0])
    return res


def flood_fill(image, sr, sc, color):
    """LC 733. No unmark: recoloring is the visited mark."""
    rows, cols = len(image), len(image[0])
    old = image[sr][sc]
    if old == color:
        return image

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or image[r][c] != old:
            return
        image[r][c] = color
        for dr, dc in DIRECTIONS:
            dfs(r + dr, c + dc)
    dfs(sr, sc)
    return image


def num_islands(grid):
    """LC 200."""
    rows, cols = len(grid), len(grid[0])

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != "1":
            return
        grid[r][c] = "0"
        for dr, dc in DIRECTIONS:
            dfs(r + dr, c + dc)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                dfs(r, c)
                count += 1
    return count


def get_maximum_gold(grid):
    """LC 1219. Start anywhere with gold; best simple path sum."""
    rows, cols = len(grid), len(grid[0])

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == 0:
            return 0
        gold = grid[r][c]
        grid[r][c] = 0
        best = 0
        for dr, dc in DIRECTIONS:
            best = max(best, dfs(r + dr, c + dc))
        grid[r][c] = gold
        return gold + best

    res = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c]:
                res = max(res, dfs(r, c))
    return res


# ------------------------------------------------------------------------ tests


def simple_paths(rows, cols, ok, starts):
    """Every simple 4-direction path (list of cells) over cells where ok(r, c)."""
    out = []

    def go(path, used):
        out.append(list(path))
        r, c = path[-1]
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and ok(nr, nc) and (nr, nc) not in used:
                path.append((nr, nc)); used.add((nr, nc))
                go(path, used)
                path.pop(); used.discard((nr, nc))

    for s in starts:
        if ok(*s):
            go([s], {s})
    return out


def rand_board(rows, cols, alphabet):
    return [[random.choice(alphabet) for _ in range(cols)] for _ in range(rows)]


def test_exist_and_find_words_vs_brute_force():
    random.seed(1)
    for _ in range(40):
        R, C = random.randint(1, 3), random.randint(1, 3)
        board = rand_board(R, C, "ab")
        spelled = {"".join(board[r][c] for r, c in p)
                   for p in simple_paths(R, C, lambda r, c: True, [(r, c) for r in range(R) for c in range(C)])}
        words = list({"".join(random.choice("ab") for _ in range(random.randint(1, 5))) for _ in range(8)})
        for w in words:
            assert exist([row[:] for row in board], w) == (w in spelled)
        assert sorted(find_words([row[:] for row in board], words)) == sorted(w for w in words if w in spelled)


def test_n_queens_vs_permutations():
    for n in range(1, 8):
        want = sorted(["".join("Q" if c == q else "." for c in range(n)) for q in perm]
                      for perm in permutations(range(n))
                      if len({r + q for r, q in enumerate(perm)}) == n == len({r - q for r, q in enumerate(perm)}))
        assert sorted(solve_n_queens(n)) == want
        assert total_n_queens(n) == len(want)


def make_sudoku(seed, holes):
    rng = random.Random(seed)
    digits = rng.sample("123456789", 9)
    solved = [[digits[(r * 3 + r // 3 + c) % 9] for c in range(9)] for r in range(9)]
    puzzle = [row[:] for row in solved]
    for r, c in rng.sample([(r, c) for r in range(9) for c in range(9)], holes):
        puzzle[r][c] = "."
    return puzzle


def test_solve_sudoku_fills_a_valid_board():
    for seed in range(5):
        puzzle = make_sudoku(seed, 50)
        board = [row[:] for row in puzzle]
        solve_sudoku(board)
        groups = [board[r] for r in range(9)] + [[board[r][c] for r in range(9)] for c in range(9)]
        groups += [[board[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)]
                   for br in (0, 3, 6) for bc in (0, 3, 6)]
        assert all(sorted(g) == list("123456789") for g in groups)
        assert all(puzzle[r][c] in (".", board[r][c]) for r in range(9) for c in range(9))


def test_unique_paths_with_obstacles_vs_product():
    assert unique_paths_with_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2
    random.seed(2)
    for _ in range(40):
        R, C = random.randint(1, 4), random.randint(1, 4)
        grid = [[int(random.random() < 0.25) for _ in range(C)] for _ in range(R)]
        want = 0
        for moves in set(permutations("D" * (R - 1) + "R" * (C - 1))):
            r = c = 0
            ok = grid[0][0] == 0
            for m in moves:
                r, c = (r + 1, c) if m == "D" else (r, c + 1)
                ok = ok and grid[r][c] == 0
            want += ok
        assert unique_paths_with_obstacles(grid) == want


def test_rat_in_maze_vs_brute_force():
    random.seed(3)
    for _ in range(40):
        n = random.randint(1, 4)
        grid = [[int(random.random() < 0.75) for _ in range(n)] for _ in range(n)]
        paths = [p for p in simple_paths(n, n, lambda r, c: grid[r][c] == 1, [(0, 0)])
                 if p[-1] == (n - 1, n - 1)] if grid[n - 1][n - 1] else []
        name = {(1, 0): "D", (0, -1): "L", (0, 1): "R", (-1, 0): "U"}
        want = sorted("".join(name[(b[0] - a[0], b[1] - a[1])] for a, b in zip(p, p[1:])) for p in paths)
        assert sorted(rat_in_maze(grid)) == want


def test_unique_paths_iii_vs_brute_force():
    assert unique_paths_iii([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 2, -1]]) == 2
    random.seed(4)
    for _ in range(40):
        R, C = random.randint(1, 3), random.randint(2, 4)
        cells = [(r, c) for r in range(R) for c in range(C)]
        s, e = random.sample(cells, 2)
        grid = [[-1 if random.random() < 0.2 else 0 for _ in range(C)] for _ in range(R)]
        grid[s[0]][s[1]], grid[e[0]][e[1]] = 1, 2
        need = sum(v != -1 for row in grid for v in row)
        want = sum(1 for p in simple_paths(R, C, lambda r, c: grid[r][c] != -1, [s])
                   if p[-1] == e and len(p) == need)
        assert unique_paths_iii([row[:] for row in grid]) == want


def test_all_paths_source_target():
    assert sorted(all_paths_source_target([[1, 2], [3], [3], []])) == [[0, 1, 3], [0, 2, 3]]
    random.seed(5)
    for _ in range(30):
        n = random.randint(2, 7)
        graph = [[v for v in range(u + 1, n) if random.random() < 0.5] for u in range(n)]
        want = []
        for bits in product([0, 1], repeat=n - 2):
            p = [0] + [i + 1 for i, b in enumerate(bits) if b] + [n - 1]
            if all(b in graph[a] for a, b in zip(p, p[1:])):
                want.append(p)
        assert sorted(all_paths_source_target(graph)) == sorted(want)


def test_flood_fill_and_islands_vs_bfs():
    random.seed(6)
    for _ in range(40):
        R, C = random.randint(1, 6), random.randint(1, 6)
        grid = [[random.choice("01") for _ in range(C)] for _ in range(R)]
        # union-find count
        parent = {(r, c): (r, c) for r in range(R) for c in range(C) if grid[r][c] == "1"}

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x
        for (r, c) in list(parent):
            for nr, nc in ((r + 1, c), (r, c + 1)):
                if (nr, nc) in parent:
                    parent[find((r, c))] = find((nr, nc))
        want = len({find(x) for x in parent})
        assert num_islands([row[:] for row in grid]) == want

        image = [[int(v) for v in row] for row in grid]
        sr, sc = random.randrange(R), random.randrange(C)
        old = image[sr][sc]
        region = {p[-1] for p in simple_paths(R, C, lambda r, c: image[r][c] == old, [(sr, sc)])}
        out = flood_fill([row[:] for row in image], sr, sc, 7)
        assert all(out[r][c] == (7 if (r, c) in region else image[r][c]) for r in range(R) for c in range(C))


def test_get_maximum_gold_vs_brute_force():
    assert get_maximum_gold([[0, 6, 0], [5, 8, 7], [0, 9, 0]]) == 24
    random.seed(7)
    for _ in range(40):
        R, C = random.randint(1, 3), random.randint(1, 4)
        grid = [[random.choice([0, 0, 1, 3, 5]) for _ in range(C)] for _ in range(R)]
        paths = simple_paths(R, C, lambda r, c: grid[r][c] > 0, [(r, c) for r in range(R) for c in range(C)])
        want = max([sum(grid[r][c] for r, c in p) for p in paths], default=0)
        assert get_maximum_gold([row[:] for row in grid]) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
