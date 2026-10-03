"""Permutations — all orderings, with and without duplicate values.

Signs: "all arrangements", "every order", "all possible sequences using each
       element once", n <= ~9 (9! = 362,880).
Approach: each level fills the next position with any unused element. Track
          use with a `used` boolean list (or a bitmask int). Complete when the
          path has n elements.
          Duplicates: sort, then skip nums[i] if it equals nums[i-1] and
          nums[i-1] is *not* used — that forces equal values to be placed in
          index order, so each distinct arrangement is built once.
          Swap variant: swap nums[i] into position `first`, recurse, swap back.
          No extra memory, but output order is not lexicographic.
Complexity: O(n! * n) time and output.
Gotchas:
  - Dup skip condition is `not used[i-1]`. `used[i-1]` also dedupes but prunes
    later (deeper), so it explores far more of the tree.
  - The swap variant cannot dedupe with the sorted-neighbour trick, because
    swapping breaks the sort. Use a per-level `seen` set there.
  - Counting only (no list)? n!/(c1! c2! ...) — no search needed.

Run the tests at the bottom with:  python3 backtracking/permutations.py
"""

import random
from itertools import permutations as it_perms
from math import factorial, prod
from collections import Counter


# ---------------------------------------------------------------- implementation


def permute(nums):
    """All n! orderings of distinct values, in lexicographic index order."""
    n, out, path, used = len(nums), [], [], [False] * len(nums)

    def go():
        if len(path) == n:
            out.append(path[:])
            return
        for i in range(n):
            if used[i]:
                continue
            used[i] = True; path.append(nums[i])
            go()
            used[i] = False; path.pop()
    go()
    return out


def permute_unique(nums):
    """All distinct orderings when nums may repeat values."""
    nums = sorted(nums)
    n, out, path, used = len(nums), [], [], [False] * len(nums)

    def go():
        if len(path) == n:
            out.append(path[:])
            return
        for i in range(n):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue                  # equal values go in index order
            used[i] = True; path.append(nums[i])
            go()
            used[i] = False; path.pop()
    go()
    return out


def permute_swap(nums):
    """In-place swap variant; dedupes with a per-level seen set."""
    a, out = list(nums), []

    def go(first):
        if first == len(a):
            out.append(a[:])
            return
        seen = set()
        for i in range(first, len(a)):
            if a[i] in seen:
                continue
            seen.add(a[i])
            a[first], a[i] = a[i], a[first]
            go(first + 1)
            a[first], a[i] = a[i], a[first]
    go(0)
    return out


def permute_bitmask(nums):
    """Same as permute, with an int as the used-set."""
    n, out, path = len(nums), [], []

    def go(mask):
        if mask == (1 << n) - 1:
            out.append(path[:])
            return
        for i in range(n):
            if mask >> i & 1:
                continue
            path.append(nums[i])
            go(mask | 1 << i)             # no undo needed: mask is passed by value
            path.pop()
    go(0)
    return out


# ------------------------------------------------------------------------ tests


def test_permute_matches_itertools_in_order():
    for n in range(0, 7):
        nums = list(range(n))
        want = [list(p) for p in it_perms(nums)]
        assert permute(nums) == want
        assert permute_bitmask(nums) == want


def test_permute_unique_classic():
    assert permute_unique([1, 1, 2]) == [[1, 1, 2], [1, 2, 1], [2, 1, 1]]


def test_permute_unique_random_vs_itertools():
    random.seed(3)
    for _ in range(40):
        nums = [random.randint(0, 3) for _ in range(random.randint(0, 7))]
        want = sorted(set(it_perms(nums)))
        got = permute_unique(nums)
        assert [tuple(p) for p in got] == want      # already sorted, no dups
        assert sorted(map(tuple, permute_swap(nums))) == want
        c = Counter(nums)
        assert len(got) == factorial(len(nums)) // prod(factorial(v) for v in c.values())


def test_used_prev_variant_is_correct_but_slower():
    def run(nums, prune_on_unused):
        nums, n = sorted(nums), len(nums)
        out, path, used, calls = [], [], [False] * n, [0]

        def go():
            calls[0] += 1
            if len(path) == n:
                out.append(tuple(path)); return
            for i in range(n):
                if used[i]:
                    continue
                if i > 0 and nums[i] == nums[i - 1] and (used[i - 1] != prune_on_unused):
                    continue
                used[i] = True; path.append(nums[i]); go(); used[i] = False; path.pop()
        go()
        return sorted(out), calls[0]

    nums = [1, 1, 1, 1, 2, 2]
    a, fast = run(nums, True)    # skip when previous equal is unused
    b, slow = run(nums, False)   # skip when previous equal is used
    assert a == b == sorted(set(it_perms(nums)))
    assert fast < slow


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
