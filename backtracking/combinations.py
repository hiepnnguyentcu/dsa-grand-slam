"""Combinations and combination sum I / II / III.

Signs: "choose k of n", "all combinations that sum to target", "each number
       used once / unlimited times", result order does not matter.
Approach: for-loop tree with `start`, like subsets, but record only at the
          goal (length k, or remaining == 0).
            - combine(n, k): next pick from start..n; stop when k picked.
            - Sum I (reuse allowed): recurse with start = i, not i + 1.
            - Sum II (each index once, values repeat): sort, recurse with
              i + 1, skip equal siblings (i > start and a[i] == a[i-1]).
            - Sum III (k distinct digits 1..9 summing to n): combine + sum.
          Prune: sort candidates ascending, then `break` (not continue) as
          soon as a candidate exceeds the remaining target — every later one
          is larger too. For combine, stop when too few numbers remain.
Complexity: combine is O(C(n, k) * k). Sum I is exponential in target/min;
            pruning is what keeps it practical.
Gotchas:
  - Reuse vs no reuse is one character: go(i) vs go(i + 1).
  - Recursing from 0 instead of `start` produces permutations of each
    combination ([2,3] and [3,2]).
  - `break` on overshoot requires sorted input; on unsorted input it silently
    drops answers.
  - Need only the *number* of combinations? That is knapsack counting
    (dynamic_programming/knapsack.py), not this.

Run the tests at the bottom with:  python3 backtracking/combinations.py
"""

import random
from itertools import combinations, combinations_with_replacement


# ---------------------------------------------------------------- implementation


def combine(n, k):
    """All k-subsets of 1..n, in lexicographic order."""
    out, path = [], []

    def go(start):
        if len(path) == k:
            out.append(path[:])
            return
        need = k - len(path)
        for x in range(start, n - need + 2):  # leave room for the rest
            path.append(x)
            go(x + 1)
            path.pop()
    go(1)
    return out


def combination_sum(cands, target):
    """Sum I: distinct candidates, each reusable any number of times."""
    cands = sorted(cands)
    out, path = [], []

    def go(start, rem):
        if rem == 0:
            out.append(path[:])
            return
        for i in range(start, len(cands)):
            if cands[i] > rem:
                break                         # sorted: the rest are bigger
            path.append(cands[i])
            go(i, rem - cands[i])             # i, not i + 1: reuse allowed
            path.pop()
    go(0, target)
    return out


def combination_sum2(cands, target):
    """Sum II: candidates may repeat; each index used at most once."""
    cands = sorted(cands)
    out, path = [], []

    def go(start, rem):
        if rem == 0:
            out.append(path[:])
            return
        for i in range(start, len(cands)):
            if cands[i] > rem:
                break
            if i > start and cands[i] == cands[i - 1]:
                continue                      # equal sibling: same subtree
            path.append(cands[i])
            go(i + 1, rem - cands[i])
            path.pop()
    go(0, target)
    return out


def combination_sum3(k, n):
    """Sum III: k distinct digits from 1..9 summing to n."""
    out, path = [], []

    def go(start, rem):
        if len(path) == k:
            if rem == 0:
                out.append(path[:])
            return
        for d in range(start, 10):
            if d > rem:
                break
            path.append(d)
            go(d + 1, rem - d)
            path.pop()
    go(1, n)
    return out


# ------------------------------------------------------------------------ tests


def test_combine_matches_itertools():
    for n in range(0, 9):
        for k in range(0, n + 1):
            assert combine(n, k) == [list(c) for c in combinations(range(1, n + 1), k)]


def test_combination_sum_classic():
    assert combination_sum([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]
    assert combination_sum([2], 1) == []


def test_combination_sum_random_vs_brute_force():
    random.seed(4)
    for _ in range(40):
        cands = random.sample(range(2, 12), random.randint(1, 5))
        target = random.randint(1, 20)
        want = sorted(list(c) for r in range(1, target // min(cands) + 1)
                      for c in combinations_with_replacement(sorted(cands), r)
                      if sum(c) == target)
        assert sorted(combination_sum(cands, target)) == want


def test_combination_sum2_classic():
    assert combination_sum2([10, 1, 2, 7, 6, 1, 5], 8) == [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]


def test_combination_sum2_random_vs_brute_force():
    random.seed(5)
    for _ in range(60):
        cands = [random.randint(1, 6) for _ in range(random.randint(0, 10))]
        target = random.randint(1, 15)
        want = sorted({tuple(sorted(c)) for r in range(len(cands) + 1)
                       for c in combinations(cands, r) if sum(c) == target})
        got = combination_sum2(cands, target)
        assert [tuple(c) for c in got] == want   # sorted, no duplicates


def test_combination_sum3_vs_brute_force():
    for k in range(1, 10):
        for n in range(1, 46):
            want = [list(c) for c in combinations(range(1, 10), k) if sum(c) == n]
            assert combination_sum3(k, n) == want
    assert combination_sum3(3, 9) == [[1, 2, 6], [1, 3, 5], [2, 3, 4]]


def test_break_needs_sorted_input():
    # Unsorted + break drops answers: 5 > 4 stops the loop before reaching 1, 3.
    cands, out, path = [5, 1, 3], [], []

    def go(start, rem):
        if rem == 0:
            out.append(path[:]); return
        for i in range(start, len(cands)):
            if cands[i] > rem:
                break
            path.append(cands[i]); go(i + 1, rem - cands[i]); path.pop()
    go(0, 4)
    assert out == []
    assert combination_sum2(cands, 4) == [[1, 3]]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
