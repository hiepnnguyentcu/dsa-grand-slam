"""Pruning — make the same search tree smaller.

Signs: a correct backtracking solution times out; n around 15-25; "partition
       into k equal-sum subsets", "matchsticks to square", "fair cookie
       distribution".
Approach: four standard cuts, shown on k equal-sum subsets.
            1. Bound: reject early when the target is not an integer or any
               item exceeds it.
            2. Sort descending: big items fail fast, so bad branches die near
               the root.
            3. Symmetry: buckets with the same current load are
               interchangeable; try an item in only one of them. In
               particular, if it failed in an empty bucket, it fails in every
               empty bucket — stop.
            4. Memoise failed states: with a bitmask of used items, the
               remaining work depends only on the mask (the current bucket
               load is sum(mask) % target). Record masks that failed and
               never expand them again. This turns the search into bitmask
               DP over 2^n states.
          Bitmask used-sets (an int instead of a list of bools) make 3 and 4
          cheap: the mask is hashable and passed by value.
Complexity: bucket search worst case O(k^n); memoised mask search
            O(2^n * n).
Gotchas:
  - Memoising requires the future to depend only on the key. A mask works for
    k-partition because the bucket load is derivable from it; it would not
    work if bucket *identity* mattered.
  - Sort first, then `break` on overshoot; `continue` would also be correct
    but skips the pruning.
  - Once the memo covers every state, you are doing DP. If you only need a
    yes/no, count or optimum, start from dynamic_programming/ instead.

Run the tests at the bottom with:  python3 backtracking/pruning.py
"""

import random
from functools import cache
from itertools import product


# ---------------------------------------------------------------- implementation


def can_partition_k_buckets(nums, k):
    """k equal-sum subsets by filling k buckets; cuts 1-3 above."""
    total = sum(nums)
    if k <= 0 or total % k:
        return False
    target = total // k
    nums = sorted(nums, reverse=True)          # cut 2
    if nums and nums[0] > target:              # cut 1
        return False
    load = [0] * k

    def go(i):
        if i == len(nums):
            return True                        # all loads equal target by construction
        tried = set()
        for b in range(k):
            if load[b] + nums[i] > target or load[b] in tried:
                continue                       # cut 3: equal loads are symmetric
            tried.add(load[b])
            load[b] += nums[i]
            if go(i + 1):
                return True
            load[b] -= nums[i]
        return False
    return go(0)


def can_partition_k_mask(nums, k):
    """k equal-sum subsets via used-bitmask + memo of failed masks (cut 4)."""
    total, n = sum(nums), len(nums)
    if k <= 0 or total % k:
        return False
    target = total // k
    nums = sorted(nums, reverse=True)
    if nums and nums[0] > target:
        return False
    full = (1 << n) - 1

    @cache
    def go(mask, cur):                         # cur = sum(mask) % target, a function of mask
        if mask == full:
            return True
        for i in range(n):
            if mask >> i & 1 or cur + nums[i] > target:
                continue
            if go(mask | 1 << i, (cur + nums[i]) % target):
                return True
            if cur == 0:
                return False                   # failed as a bucket's first item: hopeless
        return False
    return go(0, 0)


def matchsticks_square(sticks):
    """Can all sticks form a square? k-partition with k = 4."""
    return len(sticks) >= 4 and can_partition_k_buckets(sticks, 4)


def combination_count_calls(cands, target, prune):
    """Count recursive calls for combination sum, with or without sort + break."""
    cands = sorted(cands) if prune else list(cands)
    calls = [0]

    def go(start, rem):
        calls[0] += 1
        if rem <= 0:
            return
        for i in range(start, len(cands)):
            if prune and cands[i] > rem:
                break
            go(i, rem - cands[i])
    go(0, target)
    return calls[0]


# ------------------------------------------------------------------------ tests


def brute_k_partition(nums, k):
    """Try every assignment of items to buckets."""
    if k <= 0:
        return False
    for assign in product(range(k), repeat=len(nums)):
        sums = [0] * k
        for x, b in zip(nums, assign):
            sums[b] += x
        if len(set(sums)) == 1:
            return True
    return False


def test_classic_cases():
    assert can_partition_k_buckets([4, 3, 2, 3, 5, 2, 1], 4)
    assert can_partition_k_mask([4, 3, 2, 3, 5, 2, 1], 4)
    assert not can_partition_k_buckets([1, 2, 3, 4], 3)
    assert not can_partition_k_mask([1, 2, 3, 4], 3)
    assert matchsticks_square([1, 1, 2, 2, 2])
    assert not matchsticks_square([3, 3, 3, 3, 4])


def test_both_versions_match_brute_force():
    random.seed(15)
    for _ in range(150):
        n = random.randint(1, 7)
        k = random.randint(1, 4)
        nums = [random.randint(1, 6) for _ in range(n)]
        want = brute_k_partition(nums, k)
        assert can_partition_k_buckets(nums, k) == want
        assert can_partition_k_mask(nums, k) == want


def test_versions_agree_on_larger_inputs():
    random.seed(16)
    for _ in range(30):
        n = random.randint(8, 14)
        k = random.randint(2, 5)
        nums = [random.randint(1, 10) for _ in range(n)]
        assert can_partition_k_buckets(nums, k) == can_partition_k_mask(nums, k)


def test_hard_no_case_is_fast():
    # 16 items, total divisible by 4, but no partition exists. Without the
    # symmetry cut this explores ~4^16 branches; with it, it returns at once.
    nums = [10] * 15 + [6]
    assert sum(nums) % 4 == 0
    assert not can_partition_k_buckets(nums, 4)
    assert not can_partition_k_mask(nums, 4)


def test_sort_and_break_prunes_calls():
    cands, target = [9, 8, 7, 3, 2], 30
    assert combination_count_calls(cands, target, prune=True) < combination_count_calls(cands, target, prune=False)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
