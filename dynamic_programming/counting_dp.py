"""Counting DP — modulo counting (dice, knight dialer) and Catalan structures.

Signs: "return the answer modulo 10^9 + 7", number of sequences following
       adjacency rules, dice sums, number of BST shapes, valid parentheses,
       polygon triangulations, full binary trees.
Approach:
  - Sequences: state = (length, last element or running sum). Each new state
    sums the counts of every compatible old state; reduce mod on every add.
    When a transition sums a *range* of old states, use prefix sums so it is
    O(1) instead of O(range).
  - Catalan: pick the root / first split. Left and right sides are independent,
    so C[n] = sum C[i] * C[n - 1 - i] over i. Closed form C(2n, n) / (n + 1).
Complexity: dice O(n * target); knight O(n * 10); Catalan O(n^2) or O(n).
Gotchas:
  - Python ints do not overflow, so a forgotten `% MOD` gives the right answer
    slowly on small inputs and huge numbers on large ones. Tests on big n
    catch it.
  - Prefix-sum subtraction can go negative before the mod; Python's % keeps
    the result in [0, MOD), other languages' does not.
  - Knight dialer: n = 1 counts all ten digits, including 5, which has no
    moves. n = 0 is zero numbers.

Run the tests at the bottom with:  python3 dynamic_programming/counting_dp.py
"""

import random
from itertools import product
from math import comb


MOD = 10**9 + 7


# ---------------------------------------------------------------- implementation


def dice_ways(n, faces, target, mod=MOD):
    """Ways for n dice with `faces` faces each to sum to target."""
    dp = [1] + [0] * target  # zero dice: only the sum 0
    for _ in range(n):
        pre = [0]
        for v in dp:
            pre.append((pre[-1] + v) % mod)
        ndp = [0] * (target + 1)
        for t in range(1, target + 1):
            lo = max(0, t - faces)
            ndp[t] = (pre[t] - pre[lo]) % mod  # dp[t - faces] + ... + dp[t - 1]
        dp = ndp
    return dp[target] % mod


KNIGHT_MOVES = {
    0: (4, 6), 1: (6, 8), 2: (7, 9), 3: (4, 8), 4: (0, 3, 9),
    5: (), 6: (0, 1, 7), 7: (2, 6), 8: (1, 3), 9: (2, 4),
}


def knight_dialer(n, mod=MOD):
    """Distinct n-digit numbers a chess knight can dial on a phone pad."""
    if n <= 0:
        return 0
    dp = [1] * 10
    for _ in range(n - 1):
        ndp = [0] * 10
        for d in range(10):
            for nd in KNIGHT_MOVES[d]:
                ndp[nd] = (ndp[nd] + dp[d]) % mod
        dp = ndp
    return sum(dp) % mod


def num_bst_shapes(n):
    """Catalan number C[n]: structurally distinct BSTs on n keys."""
    C = [1] + [0] * n
    for k in range(1, n + 1):
        C[k] = sum(C[i] * C[k - 1 - i] for i in range(k))  # root is key i + 1
    return C[n]


def catalan_formula(n):
    return comb(2 * n, n) // (n + 1)


# ------------------------------------------------------------------------ tests


def balanced_parens(n):
    """Brute force: every string of n '(' and n ')' that never dips below 0."""
    count = 0
    for s in product("()", repeat=2 * n):
        depth = 0
        for ch in s:
            depth += 1 if ch == "(" else -1
            if depth < 0:
                break
        else:
            count += depth == 0
    return count


def bst_shapes(lo, hi):
    """Brute force: actually build every BST shape on keys lo..hi."""
    if lo > hi:
        return [None]
    return [
        (root, left, right)
        for root in range(lo, hi + 1)
        for left in bst_shapes(lo, root - 1)
        for right in bst_shapes(root + 1, hi)
    ]


def test_dice_classic():
    assert dice_ways(1, 6, 3) == 1
    assert dice_ways(2, 6, 7) == 6
    assert dice_ways(2, 5, 10) == 1
    assert dice_ways(30, 30, 500) == 222616187
    assert dice_ways(0, 6, 0) == 1


def test_dice_matches_enumeration():
    random.seed(140)
    for _ in range(100):
        n, faces = random.randint(0, 4), random.randint(1, 6)
        target = random.randint(0, n * faces + 2)
        brute = sum(1 for roll in product(range(1, faces + 1), repeat=n) if sum(roll) == target)
        assert dice_ways(n, faces, target) == brute
        assert dice_ways(n, faces, target, mod=7) == brute % 7


def test_knight_dialer():
    assert knight_dialer(0) == 0
    assert knight_dialer(1) == 10
    assert knight_dialer(2) == 20
    assert knight_dialer(3131) == 136006598
    # brute force: walk every dialable number
    for n in range(1, 7):
        seqs = [[d] for d in range(10)]
        for _ in range(n - 1):
            seqs = [s + [nd] for s in seqs for nd in KNIGHT_MOVES[s[-1]]]
        assert knight_dialer(n) == len(seqs)


def test_forgetting_mod_is_the_trap():
    # Without the mod Python still gets it right, just as a huge integer.
    # (Don't pass mod=float("inf"): int % inf is a float and loses precision.)
    dp = [1] * 10
    for _ in range(3131 - 1):
        dp = [sum(dp[p] for p in KNIGHT_MOVES[d]) for d in range(10)]  # moves are symmetric
    exact = sum(dp)
    assert len(str(exact)) > 1000
    assert exact % MOD == knight_dialer(3131)


def test_catalan():
    first = [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862]
    assert [num_bst_shapes(n) for n in range(10)] == first
    for n in range(8):
        assert num_bst_shapes(n) == catalan_formula(n) == len(bst_shapes(1, n))
    for n in range(7):
        assert balanced_parens(n) == num_bst_shapes(n)
    for n in range(60):
        assert num_bst_shapes(n) == catalan_formula(n)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
