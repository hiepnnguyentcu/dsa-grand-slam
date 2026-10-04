"""Target enumeration — factor combinations, dice rolls to a target.

Signs: "all ways to make target", "every factorisation", "number of ways to
       roll / pick so the total is target".
Approach: same tree as combination sum; what changes is the order rule.
            order doesn't matter (254, 39, 40, 216): loop from start ->
              start is a choice. 254: next factor >= current factor.
            order matters (1155, 377, 494): each position is a slot ->
              loop over all choices, start + 1.
          The combination-sum family itself lives in combinations.py; 494 in
          string_construction.py.
Complexity: exponential; 1155 backtracking is k^n — DP makes it n * k * target.
Gotchas:
  - 254: loop factor up to sqrt(remaining) only; the leftover `remaining`
    is the last factor. Exclude [n] itself.
  - 1155: prune when curr_sum + (dice left) > target or
    curr_sum + k * (dice left) < target.
  - Counts at real sizes -> DP (dynamic_programming/knapsack.py).

Run the tests at the bottom with:  python3 backtracking/target_enumeration.py
"""

import random
from itertools import combinations_with_replacement, product
from math import prod


# ---------------------------------------------------------------- implementation


def get_factors(n):
    """LC 254. All factorisations of n into factors >= 2, excluding [n]."""
    res = []

    def dfs(start, res, temp, remaining):
        factor = start
        while factor * factor <= remaining:
            if remaining % factor == 0:
                temp.append(factor)
                res.append(temp + [remaining // factor])
                dfs(factor, res, temp, remaining // factor)
                temp.pop()
            factor += 1

    dfs(2, res, [], n)
    return res


def num_rolls_to_target(n, k, target):
    """LC 1155. n dice, faces 1..k; ordered rolls summing to target."""
    def dfs(start, curr_sum):
        left = n - start
        if curr_sum + left > target or curr_sum + k * left < target:
            return 0
        if start == n:
            return 1
        count = 0
        for face in range(1, k + 1):
            count += dfs(start + 1, curr_sum + face)
        return count
    return dfs(0, 0)


# ------------------------------------------------------------------------ tests


def test_get_factors_vs_brute_force():
    assert get_factors(1) == [] and get_factors(37) == []
    assert sorted(get_factors(12)) == [[2, 2, 3], [2, 6], [3, 4]]
    for n in range(2, 200):
        divisors = [d for d in range(2, n) if n % d == 0]
        want = {c for r in range(2, 8) for c in combinations_with_replacement(divisors, r) if prod(c) == n}
        got = get_factors(n)
        assert len(got) == len(want) and set(map(tuple, got)) == want


def test_num_rolls_to_target_vs_product():
    assert num_rolls_to_target(1, 6, 3) == 1
    assert num_rolls_to_target(2, 6, 7) == 6
    random.seed(1)
    for _ in range(40):
        n, k = random.randint(1, 4), random.randint(1, 6)
        target = random.randint(1, n * k + 1)
        want = sum(sum(p) == target for p in product(range(1, k + 1), repeat=n))
        assert num_rolls_to_target(n, k, target) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
