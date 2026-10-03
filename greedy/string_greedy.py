"""String greedy — a custom order, or a range of possible states.

Signs: "arrange numbers to form the largest number", "is this string with '*'
       wildcards a valid bracket sequence", "fewest insertions to balance".
Approach:
  - Largest number: sort with the comparator "a before b iff a + b > b + a"
    (as strings). That order is transitive, and an adjacent swap argument
    shows any out-of-order pair can be swapped to grow the result.
  - Wildcard brackets: don't branch on what '*' means. Track the range
    [lo, hi] of possible open counts: '(' raises both, ')' lowers both, '*'
    lowers lo and raises hi. Fail if hi < 0; clamp lo at 0; valid iff lo == 0
    at the end.
  - Min additions: count unmatched ')' as you go (each needs a '(' inserted)
    plus whatever '(' is still open at the end.
Complexity: largest number O(n log n * L) for L-digit strings; brackets O(n).
Gotchas:
  - Largest number: all zeros -> "0", not "000".
  - Largest number: comparing as ints (or by length) fails — "3" vs "30" needs
    "330" > "303".
  - Wildcard: clamp lo to 0 *after* each step, or a ')' can "borrow" from a
    '*' that comes later.
  - Removal-style string greedy (remove k digits, smallest subsequence) lives
    in stacks_heaps/monotonic_greedy.py.

Run the tests at the bottom with:  python3 greedy/string_greedy.py
"""

import random
from collections import deque
from functools import cmp_to_key
from itertools import permutations, product


# ---------------------------------------------------------------- implementation


def largest_number(nums):
    """Concatenate non-negative ints in the order giving the largest number."""
    strs = sorted(map(str, nums), key=cmp_to_key(
        lambda a, b: -1 if a + b > b + a else (1 if a + b < b + a else 0)))
    out = "".join(strs)
    return "0" if out and out[0] == "0" else out


def check_valid_string(s):
    """'(', ')' and '*' (any of '(', ')' or empty). Can it be balanced?"""
    lo = hi = 0
    for c in s:
        if c == "(":
            lo, hi = lo + 1, hi + 1
        elif c == ")":
            lo, hi = lo - 1, hi - 1
        else:
            lo, hi = lo - 1, hi + 1
        if hi < 0:
            return False
        lo = max(lo, 0)
    return lo == 0


def min_add_to_make_valid(s):
    """Fewest '(' or ')' insertions to balance a bracket string."""
    open_, need = 0, 0
    for c in s:
        if c == "(":
            open_ += 1
        elif open_:
            open_ -= 1
        else:
            need += 1
    return need + open_


# ------------------------------------------------------------------------ tests


def balanced(s):
    depth = 0
    for c in s:
        depth += 1 if c == "(" else -1
        if depth < 0:
            return False
    return depth == 0


def brute_wildcard(s):
    stars = [i for i, c in enumerate(s) if c == "*"]
    for choice in product(["(", ")", ""], repeat=len(stars)):
        t = list(s)
        for i, ch in zip(stars, choice):
            t[i] = ch
        if balanced("".join(t)):
            return True
    return False


def brute_min_add(s):
    """0-1 BFS over (index, open depth): consuming s[i] is free, inserting costs 1."""
    cap = len(s) + 1
    dist = {(0, 0): 0}
    dq = deque([(0, 0)])
    while dq:
        i, d = dq.popleft()
        if i == len(s) and d == 0:
            return dist[(i, d)]
        moves = []
        if i < len(s):
            nd = d + (1 if s[i] == "(" else -1)
            if nd >= 0:
                moves.append((i + 1, nd, 0))
        if d < cap:
            moves.append((i, d + 1, 1))  # insert '('
        if d:
            moves.append((i, d - 1, 1))  # insert ')'
        for ni, nd, w in moves:
            if dist.get((ni, nd), float("inf")) > dist[(i, d)] + w:
                dist[(ni, nd)] = dist[(i, d)] + w
                (dq.appendleft if w == 0 else dq.append)((ni, nd))


def test_largest_number_examples():
    assert largest_number([10, 2]) == "210"
    assert largest_number([3, 30, 34, 5, 9]) == "9534330"
    assert largest_number([0, 0]) == "0"


def test_largest_number_matches_brute_force():
    random.seed(21)
    for _ in range(300):
        nums = [random.choice([0, 1, 3, 9, 10, 30, 34, 98, 121, 12]) for _ in range(random.randint(1, 5))]
        best = max(int("".join(map(str, p))) for p in permutations(nums))
        assert largest_number(nums) == str(best)


def test_wildcard_examples():
    assert check_valid_string("()")
    assert check_valid_string("(*)")
    assert check_valid_string("(*))")
    assert not check_valid_string(")*(")


def test_wildcard_matches_brute_force():
    random.seed(22)
    for _ in range(500):
        s = "".join(random.choice("()*") for _ in range(random.randint(0, 8)))
        assert check_valid_string(s) == brute_wildcard(s)


def test_min_add():
    assert min_add_to_make_valid("())") == 1
    assert min_add_to_make_valid("(((") == 3
    assert min_add_to_make_valid("()))((") == 4
    random.seed(23)
    for _ in range(300):
        s = "".join(random.choice("()") for _ in range(random.randint(0, 10)))
        assert min_add_to_make_valid(s) == brute_min_add(s)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
