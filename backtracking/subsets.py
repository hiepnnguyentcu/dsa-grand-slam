"""Subsets — every selection, with dups, order-preserving, summing to a target.

Signs: "all subsets", "power set", "subsequences", "can we pick some that sum to".
Approach: loop from start -> start is a choice -> recurse i+1. Every node is an
          answer, so record on entry, not only at leaves.
          Dups: sort, skip `i > start and nums[i] == nums[i-1]`.
          Can't sort (order matters, LC 491): per-call `seen` set instead.
Complexity: O(2^n * n).
Gotchas:
  - Dedup is `i > start`, not `i > 0` — `i > 0` also kills [2, 2].
  - `res.append(temp)` stores the live list; it ends up []. Use temp.copy().
  - Only need yes/no or a count (416, 2035)? That's DP / meet-in-the-middle at
    real sizes; backtracking here is the baseline.

Run the tests at the bottom with:  python3 backtracking/subsets.py
"""

import random
from itertools import combinations


# ---------------------------------------------------------------- implementation


def subsets(nums):
    """LC 78."""
    res = []

    def dfs(start, res, temp):
        res.append(temp.copy())
        for i in range(start, len(nums)):
            temp.append(nums[i])
            dfs(i + 1, res, temp)
            temp.pop()
    dfs(0, res, [])
    return res


def subset_xor_sum(nums):
    """LC 1863. Sum of XOR totals over every subset."""
    def dfs(start, curr_xor):
        total = curr_xor
        for i in range(start, len(nums)):
            total += dfs(i + 1, curr_xor ^ nums[i])
        return total
    return dfs(0, 0)


def subsets_with_dup(nums):
    """LC 90."""
    nums = sorted(nums)
    res = []

    def dfs(start, res, temp):
        res.append(temp.copy())
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            temp.append(nums[i])
            dfs(i + 1, res, temp)
            temp.pop()
    dfs(0, res, [])
    return res


def find_subsequences(nums):
    """LC 491. Non-decreasing subsequences, len >= 2. Can't sort -> per-call seen.

    seen only compares siblings (same parent, same loop):
        horizontal repeat -> skip, vertical repeat (deeper, new seen) -> allow.
    """
    res = []

    def dfs(start, res, temp):
        if len(temp) >= 2:
            res.append(temp.copy())

        seen = set()
        for i in range(start, len(nums)):
            if nums[i] in seen:
                continue
            if temp and temp[-1] > nums[i]:
                continue
            seen.add(nums[i])
            temp.append(nums[i])
            dfs(i + 1, res, temp)
            temp.pop()
    dfs(0, res, [])
    return res


def can_partition(nums):
    """LC 416. Some subset sums to total / 2."""
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    nums = sorted(nums, reverse=True)

    def dfs(start, curr_sum):
        if curr_sum == target:
            return True
        for i in range(start, len(nums)):
            if curr_sum + nums[i] > target:
                continue
            if i > start and nums[i] == nums[i - 1]:
                continue
            if dfs(i + 1, curr_sum + nums[i]):
                return True
        return False
    return dfs(0, 0)


def minimum_difference(nums):
    """LC 2035. Split 2n numbers into two halves of n; min |sum A - sum B|."""
    n = len(nums) // 2
    total = sum(nums)
    res = [float("inf")]

    def dfs(start, count, curr_sum):
        if count == n:
            res[0] = min(res[0], abs(total - 2 * curr_sum))
            return
        for i in range(start, len(nums)):
            dfs(i + 1, count + 1, curr_sum + nums[i])
    dfs(0, 0, 0)
    return res[0]


# ------------------------------------------------------------------------ tests


def canon(sets):
    return sorted(tuple(s) for s in sets)


def all_index_subsets(nums):
    return [c for r in range(len(nums) + 1) for c in combinations(nums, r)]


def test_subsets_vs_itertools():
    random.seed(1)
    for n in range(0, 9):
        nums = random.sample(range(100), n)
        got = subsets(nums)
        assert len(got) == 2 ** n
        assert canon(got) == canon(all_index_subsets(nums))


def test_subset_xor_sum():
    assert subset_xor_sum([1, 3]) == 6
    assert subset_xor_sum([5, 1, 6]) == 28
    random.seed(2)
    for _ in range(30):
        nums = [random.randint(1, 20) for _ in range(random.randint(1, 8))]
        want = 0
        for c in all_index_subsets(nums):
            x = 0
            for v in c:
                x ^= v
            want += x
        assert subset_xor_sum(nums) == want


def test_subsets_with_dup_vs_deduped_brute_force():
    assert canon(subsets_with_dup([1, 2, 2])) == canon([[], [1], [2], [1, 2], [2, 2], [1, 2, 2]])
    random.seed(3)
    for _ in range(60):
        nums = [random.randint(0, 3) for _ in range(random.randint(0, 9))]
        got = subsets_with_dup(nums)
        want = {tuple(c) for c in all_index_subsets(sorted(nums))}
        assert len(got) == len(want) == len(set(map(tuple, got)))
        assert set(map(tuple, got)) == want


def test_dedup_i_gt_0_loses_answers():
    nums, res = [2, 2], []

    def dfs(start, res, temp):
        res.append(temp.copy())
        for i in range(start, len(nums)):
            if i > 0 and nums[i] == nums[i - 1]:   # BUG
                continue
            temp.append(nums[i]); dfs(i + 1, res, temp); temp.pop()
    dfs(0, res, [])
    assert [2, 2] not in res and [2, 2] in subsets_with_dup(nums)


def test_find_subsequences_vs_brute_force():
    assert canon(find_subsequences([4, 6, 7, 7])) == canon(
        [[4, 6], [4, 6, 7], [4, 6, 7, 7], [4, 7], [4, 7, 7], [6, 7], [6, 7, 7], [7, 7]])
    random.seed(4)
    for _ in range(60):
        nums = [random.randint(-2, 3) for _ in range(random.randint(0, 9))]
        got = find_subsequences(nums)
        want = {c for c in all_index_subsets(nums)
                if len(c) >= 2 and all(a <= b for a, b in zip(c, c[1:]))}
        assert len(got) == len(want) and set(map(tuple, got)) == want


def test_can_partition_vs_brute_force():
    assert can_partition([1, 5, 11, 5]) and not can_partition([1, 2, 3, 5])
    random.seed(5)
    for _ in range(100):
        nums = [random.randint(1, 12) for _ in range(random.randint(1, 10))]
        want = any(2 * sum(c) == sum(nums) for c in all_index_subsets(nums))
        assert can_partition(nums) == want


def test_minimum_difference_vs_brute_force():
    assert minimum_difference([3, 9, 7, 3]) == 2
    assert minimum_difference([-36, 36]) == 72
    random.seed(6)
    for _ in range(40):
        n = random.randint(1, 4)
        nums = [random.randint(-20, 20) for _ in range(2 * n)]
        want = min(abs(sum(nums) - 2 * sum(c)) for c in combinations(nums, n))
        assert minimum_difference(nums) == want


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
