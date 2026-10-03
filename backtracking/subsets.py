"""Subsets — power set, with and without duplicate values.

Signs: "all subsets", "power set", "every possible selection", n <= ~20.
Approach: for-loop tree. Every node of the tree *is* a subset, so record the
          path on entry (not only at leaves). Level picks the next index
          i >= start, then recurses with start = i + 1, so each set is built
          in index order exactly once.
          Duplicates: sort, then at one level skip nums[i] when it equals
          nums[i-1] and i > start. Equal values may still stack *down* the
          tree (taking both 2s), just not as siblings (two branches that each
          start with "a 2").
          Bitmask alternative: mask 0..2^n-1, bit i means nums[i] is in.
Complexity: O(2^n * n) time and output.
Gotchas:
  - Duplicate skip is `i > start`, not `i > 0`. With `i > 0` you also block
    [2, 2], which is a valid subset.
  - The skip only works on *sorted* input — equal values must be adjacent.
  - Bitmask enumeration cannot dedupe on its own; you would need a set of
    sorted tuples, which is O(2^n) memory even when the answer is small.

Run the tests at the bottom with:  python3 backtracking/subsets.py
"""

import random
from itertools import combinations


# ---------------------------------------------------------------- implementation


def subsets(nums):
    """All 2^n subsets of distinct values."""
    out, path = [], []

    def go(start):
        out.append(path[:])               # every node is an answer
        for i in range(start, len(nums)):
            path.append(nums[i])
            go(i + 1)
            path.pop()
    go(0)
    return out


def subsets_with_dup(nums):
    """All distinct subsets when nums may repeat values."""
    nums = sorted(nums)
    out, path = [], []

    def go(start):
        out.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue                  # same value as a sibling: same subtree
            path.append(nums[i])
            go(i + 1)
            path.pop()
    go(0)
    return out


def subsets_bitmask(nums):
    """Iterative: mask -> subset. Same 2^n sets, no recursion."""
    n = len(nums)
    return [[nums[i] for i in range(n) if mask >> i & 1] for mask in range(1 << n)]


# ------------------------------------------------------------------------ tests


def canon(sets):
    return sorted(tuple(sorted(s)) for s in sets)


def reference(nums):
    """Distinct subsets via itertools, deduped by sorted tuple."""
    return sorted({tuple(sorted(c)) for r in range(len(nums) + 1) for c in combinations(nums, r)})


def test_subsets_small():
    assert canon(subsets([1, 2, 3])) == canon([[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]])
    assert subsets([]) == [[]]


def test_subsets_three_ways_agree():
    random.seed(1)
    for n in range(0, 9):
        nums = random.sample(range(100), n)
        a, b = canon(subsets(nums)), canon(subsets_bitmask(nums))
        assert a == b == reference(nums)
        assert len(a) == 2 ** n


def test_subsets_with_dup_classic():
    assert canon(subsets_with_dup([1, 2, 2])) == canon([[], [1], [2], [1, 2], [2, 2], [1, 2, 2]])


def test_subsets_with_dup_random():
    random.seed(2)
    for _ in range(60):
        nums = [random.randint(0, 3) for _ in range(random.randint(0, 9))]
        got = subsets_with_dup(nums)
        assert len(got) == len(set(map(tuple, got)))  # no duplicates emitted
        assert canon(got) == reference(nums)


def test_wrong_skip_condition_loses_answers():
    # i > 0 instead of i > start: [2, 2] disappears.
    nums, out, path = [2, 2], [], []

    def go(start):
        out.append(path[:])
        for i in range(start, len(nums)):
            if i > 0 and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i]); go(i + 1); path.pop()
    go(0)
    assert [2, 2] not in out
    assert [2, 2] in subsets_with_dup(nums)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
