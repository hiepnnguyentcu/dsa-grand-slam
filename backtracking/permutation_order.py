"""Permutation order — next / previous permutation, k-th permutation, rank.

Signs: "next greater arrangement", "next permutation", "k-th permutation",
       "which position is this permutation", n too big to enumerate n!.
Approach: no backtracking — walk the lexicographic order directly.
          next (31): from the right, find first i with nums[i] < nums[i+1]
                     (the pivot); swap it with the rightmost larger value;
                     reverse the suffix after i.
          prev-one-swap (1053): pivot = first i from the right with
                     nums[i] > nums[i+1]; swap with the largest smaller value,
                     leftmost copy of it.
          k-th (60): factorial number system — each slot has (n-1)! perms
                     per choice, so k // (n-1)! picks the digit.
          rank: inverse of 60 — count smaller unused digits per slot.
Complexity: O(n) for next/prev, O(n^2) for k-th / rank (list removal).
Gotchas:
  - 60 and rank are 1-indexed on LC: k -= 1 first.
  - 556: answer must fit in 32-bit signed int, else -1.
  - 1053 swaps with the LEFTMOST copy of the largest smaller value.
  - Permutation-in-string (567, 438) is sliding window:
    sliding_window/fixed_window.py. Cycles / min swaps (765):
    sorting/cyclic_sort.py.

Run the tests at the bottom with:  python3 backtracking/permutation_order.py
"""

import math
import random
from itertools import permutations


# ---------------------------------------------------------------- implementation


def next_permutation(nums):
    """LC 31. In place; wraps the last permutation to the first."""
    n = len(nums)
    i = n - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    if i >= 0:
        j = n - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1:] = reversed(nums[i + 1:])


def next_greater_element(n):
    """LC 556. Smallest number > n with the same digits, else -1."""
    digits = list(str(n))
    next_permutation(digits)
    res = int("".join(digits))
    return res if n < res < 2 ** 31 else -1


def prev_perm_opt1(arr):
    """LC 1053. Largest permutation < arr reachable by one swap."""
    arr = arr.copy()
    n = len(arr)
    i = n - 2
    while i >= 0 and arr[i] <= arr[i + 1]:
        i -= 1
    if i < 0:
        return arr
    j = n - 1
    while arr[j] >= arr[i]:
        j -= 1
    while arr[j - 1] == arr[j]:            # leftmost copy
        j -= 1
    arr[i], arr[j] = arr[j], arr[i]
    return arr


def get_permutation(n, k):
    """LC 60. k-th (1-indexed) permutation of 1..n."""
    digits = [str(i) for i in range(1, n + 1)]
    k -= 1
    res = []
    for slot in range(n, 0, -1):
        block = math.factorial(slot - 1)
        idx = k // block
        k %= block
        res.append(digits.pop(idx))
    return "".join(res)


def permutation_rank(perm):
    """Inverse of 60: 1-indexed rank of perm among permutations of its values."""
    remaining = sorted(perm)
    rank = 0
    for slot, x in enumerate(perm):
        idx = remaining.index(x)
        rank += idx * math.factorial(len(perm) - slot - 1)
        remaining.pop(idx)
    return rank + 1


# ------------------------------------------------------------------------ tests


def test_next_permutation_walks_lexicographic_order():
    random.seed(1)
    for n in range(1, 7):
        nums = sorted(random.sample(range(20), n))
        order = list(permutations(nums))
        cur = list(nums)
        for want in order[1:] + order[:1]:        # last wraps to first
            next_permutation(cur)
            assert tuple(cur) == want


def test_next_permutation_with_dups():
    random.seed(2)
    for _ in range(30):
        nums = sorted(random.randint(0, 2) for _ in range(random.randint(1, 6)))
        order = sorted(set(permutations(nums)))
        cur = list(nums)
        for want in order[1:]:
            next_permutation(cur)
            assert tuple(cur) == want


def test_next_greater_element():
    assert next_greater_element(12) == 21
    assert next_greater_element(21) == -1
    assert next_greater_element(2147483486) == -1
    random.seed(3)
    for _ in range(200):
        n = random.randint(1, 99999)
        bigger = [int("".join(p)) for p in permutations(str(n)) if int("".join(p)) > n]
        assert next_greater_element(n) == (min(bigger) if bigger else -1)


def test_prev_perm_opt1_vs_brute_force():
    assert prev_perm_opt1([3, 2, 1]) == [3, 1, 2]
    assert prev_perm_opt1([1, 1, 5]) == [1, 1, 5]
    assert prev_perm_opt1([1, 9, 4, 6, 7]) == [1, 7, 4, 6, 9]
    assert prev_perm_opt1([3, 1, 1, 3]) == [1, 3, 1, 3]
    random.seed(4)
    for _ in range(200):
        arr = [random.randint(1, 4) for _ in range(random.randint(1, 6))]
        cands = []
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                b = arr.copy(); b[i], b[j] = b[j], b[i]
                if b < arr:
                    cands.append(b)
        assert prev_perm_opt1(arr) == (max(cands) if cands else arr)


def test_get_permutation_and_rank_are_inverse():
    for n in range(1, 7):
        for k, p in enumerate(permutations(range(1, n + 1)), 1):
            assert get_permutation(n, k) == "".join(map(str, p))
            assert permutation_rank(list(p)) == k


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
