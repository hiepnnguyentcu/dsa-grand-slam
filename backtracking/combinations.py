"""Combinations — choose k, combination sum I/II/III.

Signs: "choose k", "all combinations", "numbers that sum to target".
Approach: loop from start -> start is a choice.
            each used once  -> dfs(i + 1)
            reuse allowed   -> dfs(i)       (LC 39)
          Stop condition is len(temp) == k, curr_sum == target, or both (216).
          Sort first so `break` on overshoot prunes the rest of the loop.
Complexity: O(C(n, k) * k) for choose-k; combination sum is exponential in
            target / min(nums).
Gotchas:
  - Reuse is dfs(i), not dfs(start) — dfs(start) also re-picks earlier
    elements and emits [2,3] and [3,2].
  - Dups (40): sort + `i > start` skip, same as subsets.
  - `break` (not continue) on overshoot only works on sorted input.
  - 377 counts ORDERED sequences: that's slot-style (loop from 0), and DP at
    real sizes (dynamic_programming/knapsack.py count_permutations).

Run the tests at the bottom with:  python3 backtracking/combinations.py
"""

import random
from itertools import combinations, combinations_with_replacement, product


# ---------------------------------------------------------------- implementation


def combine(n, k):
    """LC 77."""
    res = []

    def dfs(start, res, temp):
        if len(temp) == k:
            res.append(temp.copy())
            return
        for i in range(start, n + 1):
            if n - i + 1 < k - len(temp):       # not enough numbers left
                break
            temp.append(i)
            dfs(i + 1, res, temp)
            temp.pop()
    dfs(1, res, [])
    return res


def combination_sum(candidates, target):
    """LC 39. Distinct candidates, reuse allowed."""
    nums = sorted(candidates)
    res = []

    def dfs(start, res, temp, curr_sum):
        if curr_sum == target:
            res.append(temp.copy())
            return
        for i in range(start, len(nums)):
            if curr_sum + nums[i] > target:
                break
            temp.append(nums[i])
            dfs(i, res, temp, curr_sum + nums[i])     # i, not i+1: reuse
            temp.pop()
    dfs(0, res, [], 0)
    return res


def combination_sum4(nums, target):
    """LC 377. Count ORDERED sequences summing to target (reuse allowed)."""
    nums = sorted(nums)

    def dfs(curr_sum):
        if curr_sum == target:
            return 1
        count = 0
        for i in range(len(nums)):                    # loop from 0: order matters
            if curr_sum + nums[i] > target:
                break
            count += dfs(curr_sum + nums[i])
        return count
    return dfs(0)


def combination_sum2(candidates, target):
    """LC 40. Candidates may repeat, each used once."""
    nums = sorted(candidates)
    res = []

    def dfs(start, res, temp, curr_sum):
        if curr_sum == target:
            res.append(temp.copy())
            return
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            if curr_sum + nums[i] > target:
                break
            temp.append(nums[i])
            dfs(i + 1, res, temp, curr_sum + nums[i])
            temp.pop()
    dfs(0, res, [], 0)
    return res


def combination_sum3(k, n):
    """LC 216. k distinct digits 1-9 summing to n — two stop conditions."""
    res = []

    def dfs(start, res, temp, curr_sum):
        if len(temp) == k:
            if curr_sum == n:
                res.append(temp.copy())
            return
        for i in range(start, 10):
            if curr_sum + i > n:
                break
            temp.append(i)
            dfs(i + 1, res, temp, curr_sum + i)
            temp.pop()
    dfs(1, res, [], 0)
    return res


def find_different_binary_string(nums):
    """LC 1980. Any length-n binary string not in nums. Slot-style, stop at first."""
    n = len(nums)
    seen = set(nums)

    def dfs(start, temp):
        if start == n:
            s = "".join(temp)
            return s if s not in seen else None
        for char in ["0", "1"]:
            temp.append(char)
            found = dfs(start + 1, temp)
            if found:
                return found
            temp.pop()
        return None
    return dfs(0, [])


# ------------------------------------------------------------------------ tests


def canon(lists):
    return sorted(tuple(x) for x in lists)


def test_combine_vs_itertools():
    for n in range(1, 9):
        for k in range(1, n + 1):
            assert canon(combine(n, k)) == canon(combinations(range(1, n + 1), k))


def test_combination_sum_vs_brute_force():
    assert canon(combination_sum([2, 3, 6, 7], 7)) == [(2, 2, 3), (7,)]
    random.seed(1)
    for _ in range(40):
        cand = random.sample(range(2, 12), random.randint(1, 5))
        target = random.randint(1, 20)
        want = {c for r in range(1, target // min(cand) + 1)
                for c in combinations_with_replacement(sorted(cand), r) if sum(c) == target}
        got = combination_sum(cand, target)
        assert len(got) == len(want) and set(map(tuple, got)) == want


def test_reuse_with_dfs_start_emits_duplicates():
    nums, target, res = [2, 3], 5, []

    def dfs(start, res, temp, curr_sum):
        if curr_sum == target:
            res.append(temp.copy()); return
        for i in range(start, len(nums)):
            if curr_sum + nums[i] > target:
                break
            temp.append(nums[i]); dfs(start, res, temp, curr_sum + nums[i]); temp.pop()  # BUG
    dfs(0, res, [], 0)
    assert [2, 3] in res and [3, 2] in res
    assert combination_sum(nums, target) == [[2, 3]]


def test_combination_sum4_vs_product():
    assert combination_sum4([1, 2, 3], 4) == 7
    random.seed(2)
    for _ in range(30):
        nums = random.sample(range(1, 6), random.randint(1, 3))
        target = random.randint(1, 8)
        want = sum(1 for r in range(1, target + 1) for p in product(nums, repeat=r) if sum(p) == target)
        assert combination_sum4(nums, target) == want


def test_combination_sum2_vs_brute_force():
    assert canon(combination_sum2([10, 1, 2, 7, 6, 1, 5], 8)) == [(1, 1, 6), (1, 2, 5), (1, 7), (2, 6)]
    random.seed(3)
    for _ in range(60):
        cand = [random.randint(1, 6) for _ in range(random.randint(1, 9))]
        target = random.randint(1, 15)
        want = {c for r in range(1, len(cand) + 1) for c in combinations(sorted(cand), r) if sum(c) == target}
        got = combination_sum2(cand, target)
        assert len(got) == len(want) and set(map(tuple, got)) == want


def test_combination_sum3_vs_itertools():
    for k in range(1, 6):
        for n in range(1, 40):
            want = [c for c in combinations(range(1, 10), k) if sum(c) == n]
            assert canon(combination_sum3(k, n)) == sorted(want)


def test_find_different_binary_string():
    random.seed(4)
    for n in range(1, 9):
        for _ in range(10):
            nums = random.sample(["".join(b) for b in product("01", repeat=n)], n)
            s = find_different_binary_string(nums)
            assert len(s) == n and set(s) <= {"0", "1"} and s not in nums


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
