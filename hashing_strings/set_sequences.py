"""Set tricks — longest consecutive run in O(n), first missing positive, sudoku.

Signs: "longest consecutive sequence" with an O(n) requirement (so no sort),
       "smallest missing positive" in O(1) space, "validate a board where
       each row / column / box has no repeats", "have I been in this state
       before" (cycle in a process).
Approach: put everything in a set, then only START work where a run starts:
          x is a start iff x - 1 is not in the set. Each start walks right
          while x + 1 exists, so every value is visited at most twice.
          Missing positive: the answer is in 1..n+1, so values outside that
          range don't matter; swap each v into slot v - 1 (the array is the
          set), then the first slot i holding the wrong value gives i + 1.
          Board validation: one set of tagged keys like ("r", i, v).
Complexity: longest consecutive O(n) time, O(n) space. Missing positive O(n)
            time (each swap places one value for good), O(1) space.
Gotchas:
  - Without the "x - 1 not in set" check, longest consecutive is O(n^2).
  - Iterate the SET, not the list: duplicates in the list redo work.
  - Missing positive: the swap condition must test a[a[i] - 1] != a[i], not
    i != a[i] - 1, or duplicates loop forever.
  - Happy number's seen-set has an O(1)-space twin in
    sliding_window/fast_slow.py (Floyd).

Run the tests at the bottom with:  python3 hashing_strings/set_sequences.py
"""


# ---------------------------------------------------------------- implementation


def longest_consecutive(a):
    """LC 128. Length of the longest run of consecutive integers, any order."""
    s = set(a)
    best = 0
    for x in s:
        if x - 1 in s:          # not a run start: someone else will count it
            continue
        y = x
        while y + 1 in s:
            y += 1
        best = max(best, y - x + 1)
    return best


def longest_consecutive_runs(a):
    """All maximal runs as (start, end) pairs, sorted — same set walk."""
    s = set(a)
    runs = []
    for x in s:
        if x - 1 not in s:
            y = x
            while y + 1 in s:
                y += 1
            runs.append((x, y))
    return sorted(runs)


def first_missing_positive(a):
    """LC 41. Smallest positive integer not in a. O(1) extra space; mutates a."""
    n = len(a)
    for i in range(n):
        while 1 <= a[i] <= n and a[a[i] - 1] != a[i]:
            j = a[i] - 1
            a[i], a[j] = a[j], a[i]      # value a[i] now sits in its home slot
    for i in range(n):
        if a[i] != i + 1:
            return i + 1
    return n + 1


def is_valid_sudoku(board):
    """LC 36. Filled cells ('1'-'9', '.' empty) break no row/column/box rule."""
    seen = set()
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v == ".":
                continue
            keys = (("r", r, v), ("c", c, v), ("b", r // 3, c // 3, v))
            if any(k in seen for k in keys):
                return False
            seen.update(keys)
    return True


def is_happy(n):
    """LC 202. Seen-set cycle check: repeat n -> sum of squared digits."""
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return n == 1


# ------------------------------------------------------------------------ tests


def test_examples():
    assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4
    assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
    assert longest_consecutive([]) == 0
    assert first_missing_positive([1, 2, 0]) == 3
    assert first_missing_positive([3, 4, -1, 1]) == 2
    assert first_missing_positive([7, 8, 9, 11, 12]) == 1
    assert first_missing_positive([1, 1]) == 2          # duplicate: no infinite loop
    assert is_happy(19) and not is_happy(2)


def test_longest_consecutive_matches_sorting():
    import random

    rng = random.Random(1)
    for _ in range(500):
        a = [rng.randint(-10, 10) for _ in range(rng.randint(0, 15))]
        u = sorted(set(a))
        best = cur = 0
        for i, x in enumerate(u):
            cur = cur + 1 if i and u[i - 1] == x - 1 else 1
            best = max(best, cur)
        assert longest_consecutive(a) == best
        runs = longest_consecutive_runs(a)
        assert sorted(v for s, e in runs for v in range(s, e + 1)) == u
        assert max((e - s + 1 for s, e in runs), default=0) == best


def test_first_missing_positive_matches_brute_force():
    import random

    rng = random.Random(2)
    for _ in range(500):
        a = [rng.randint(-3, 10) for _ in range(rng.randint(0, 10))]
        expect = next(k for k in range(1, len(a) + 2) if k not in a)
        assert first_missing_positive(a[:]) == expect


def test_sudoku_matches_brute_force():
    import random

    solved = [[str((r * 3 + r // 3 + c) % 9 + 1) for c in range(9)] for r in range(9)]

    def brute(b):
        units = [[(r, c) for c in range(9)] for r in range(9)]
        units += [[(r, c) for r in range(9)] for c in range(9)]
        units += [[(br + i, bc + j) for i in range(3) for j in range(3)]
                  for br in (0, 3, 6) for bc in (0, 3, 6)]
        for u in units:
            vals = [b[r][c] for r, c in u if b[r][c] != "."]
            if len(vals) != len(set(vals)):
                return False
        return True

    assert brute(solved) and is_valid_sudoku(solved)
    rng = random.Random(3)
    for _ in range(300):
        b = [[v if rng.random() < 0.4 else "." for v in row] for row in solved]
        for _ in range(rng.randint(0, 2)):            # maybe plant a conflict
            b[rng.randrange(9)][rng.randrange(9)] = str(rng.randint(1, 9))
        assert is_valid_sudoku(b) == brute(b)


def test_happy_matches_floyd():
    def step(n):
        return sum(int(d) ** 2 for d in str(n))

    def floyd(n):
        slow, fast = n, step(n)
        while fast != 1 and slow != fast:
            slow, fast = step(slow), step(step(fast))
        return fast == 1

    for n in range(1, 1000):
        assert is_happy(n) == floyd(n)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
