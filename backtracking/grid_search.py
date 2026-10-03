"""Grid path search — word search I and II (trie).

Signs: find a word as a path of adjacent cells, each cell used at most once
       per path; "find all words from a dictionary on the board".
Approach: DFS from every cell. Mark the cell as used before recursing
          (overwrite with "#"), restore it after — choose / unchoose applied
          to the grid itself, so no visited set is needed.
            - Word search I: match word[i] at each step; stop on mismatch.
            - Word search II: put all words in a trie and walk the trie
              alongside the board. One DFS per cell serves every word at once.
              Store the full word at its end node; on a hit, record it and
              clear it so it is reported once. Prune trie leaves after use so
              dead branches stop being explored.
Complexity: word search I O(R * C * 3^L) — 4 moves at the first step, 3 after
            (you cannot go back). Word search II O(R * C * 3^Lmax), shared
            across all words, plus O(total letters) to build the trie.
Gotchas:
  - Restore the cell on *every* exit path, including after a success when you
    keep searching.
  - Running word search I once per dictionary word is the slow path the trie
    exists to avoid.
  - Early exits for word search I: word longer than R * C, or the board lacks
    enough of some letter. Searching from the rarer end (reverse the word if
    its last letter is rarer) cuts the tree a lot.
  - This is not BFS: shortest-path questions on a grid belong in graphs/.

Run the tests at the bottom with:  python3 backtracking/grid_search.py
"""

import random
from collections import Counter


DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


# ---------------------------------------------------------------- implementation


def exist(board, word):
    """True if word can be traced through adjacent cells, no cell reused."""
    R, C = len(board), len(board[0])
    if len(word) > R * C:
        return False
    have = Counter(ch for row in board for ch in row)
    if any(have[ch] < k for ch, k in Counter(word).items()):
        return False
    if have[word[0]] > have[word[-1]]:
        word = word[::-1]                     # start from the rarer letter

    def go(r, c, i):
        if board[r][c] != word[i]:
            return False
        if i == len(word) - 1:
            return True
        ch, board[r][c] = board[r][c], "#"    # choose: mark used
        found = any(0 <= r + dr < R and 0 <= c + dc < C and go(r + dr, c + dc, i + 1)
                    for dr, dc in DIRS)
        board[r][c] = ch                      # unchoose: restore
        return found

    return any(go(r, c, 0) for r in range(R) for c in range(C))


def find_words(board, words):
    """All dictionary words present on the board (each reported once)."""
    root = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = w                         # full word at its end node

    R, C, out = len(board), len(board[0]), []

    def go(r, c, parent):
        ch = board[r][c]
        node = parent.get(ch)
        if node is None:
            return
        if "$" in node:
            out.append(node.pop("$"))         # report once
        board[r][c] = "#"
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and board[nr][nc] != "#":
                go(nr, nc, node)
        board[r][c] = ch
        if not node:
            parent.pop(ch)                    # prune exhausted branch

    for r in range(R):
        for c in range(C):
            go(r, c, root)
    return out


# ------------------------------------------------------------------------ tests


def brute_paths(board, max_len):
    """Every string spelled by a simple path of length <= max_len."""
    R, C, seen = len(board), len(board[0]), set()

    def go(r, c, used, s):
        s += board[r][c]
        seen.add(s)
        if len(s) == max_len:
            return
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in used:
                go(nr, nc, used | {(nr, nc)}, s)

    for r in range(R):
        for c in range(C):
            go(r, c, {(r, c)}, "")
    return seen


BOARD = [list("ABCE"), list("SFCS"), list("ADEE")]


def test_exist_classic():
    assert exist([row[:] for row in BOARD], "ABCCED")
    assert exist([row[:] for row in BOARD], "SEE")
    assert not exist([row[:] for row in BOARD], "ABCB")   # would reuse B


def test_exist_restores_board():
    b = [row[:] for row in BOARD]
    exist(b, "ABCCED"); exist(b, "ZZZ"); exist(b, "ABCB")
    assert b == BOARD


def test_exist_random_vs_brute_force():
    random.seed(13)
    for _ in range(30):
        R, C = random.randint(1, 3), random.randint(1, 4)
        board = [[random.choice("ab") for _ in range(C)] for _ in range(R)]
        spelled = brute_paths(board, 5)
        for _ in range(10):
            w = "".join(random.choice("ab") for _ in range(random.randint(1, 5)))
            assert exist([row[:] for row in board], w) == (w in spelled)


def test_find_words_classic():
    board = [list("oaan"), list("etae"), list("ihkr"), list("iflv")]
    got = find_words([row[:] for row in board], ["oath", "pea", "eat", "rain"])
    assert sorted(got) == ["eat", "oath"]


def test_find_words_agrees_with_exist():
    random.seed(14)
    for _ in range(25):
        R, C = random.randint(1, 4), random.randint(1, 4)
        board = [[random.choice("abc") for _ in range(C)] for _ in range(R)]
        words = list({"".join(random.choice("abc") for _ in range(random.randint(1, 5)))
                      for _ in range(15)})
        got = find_words([row[:] for row in board], words)
        assert len(got) == len(set(got))                 # reported once
        assert sorted(got) == sorted(w for w in words if exist([row[:] for row in board], w))


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
