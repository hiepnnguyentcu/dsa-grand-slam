"""Selection — k-th element without a full sort: quickselect, median of medians.

Signs: "k-th largest/smallest", "median", "top k (any order)", "k closest",
       wiggle sort II (needs the median), O(n) asked and k is not tiny.
Approach: partition like quicksort, then keep only the side that holds index
          k. Iterative: shrink [lo, hi] until the pivot lands on k.
          Median of medians picks a pivot guaranteed to be in the middle 30-70%
          (groups of 5, median of their medians), so worst case is O(n).
          The 3-way version with a heap alternative is in stacks_heaps/top_k.py;
          this file uses Lomuto to show the "pivot index == k" stop.
Complexity: quickselect O(n) expected, O(n^2) worst, O(1) extra (iterative).
            Median of medians O(n) worst, big constant — rarely faster.
            Heap of size k: O(n log k); sort: O(n log n).
Gotchas:
  - k-th LARGEST is index n - k in ascending order. Convert once, up front.
  - Random pivot, or sorted input goes quadratic.
  - Lomuto + many duplicates is quadratic; use 3-way (see top_k.py).
  - Quickselect mutates; copy if the caller needs the input.
  - After select(k), a[:k] holds the k smallest in ARBITRARY order.

Run the tests at the bottom with:  python3 sorting/selection.py
"""

import random
from itertools import permutations


# ---------------------------------------------------------------- implementation


def _partition(a, lo, hi):
    r = random.randint(lo, hi)
    a[r], a[hi] = a[hi], a[r]
    pivot, i = a[hi], lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i


def quickselect(a, k):
    """Rearrange a in place so a[k] is the k-th smallest (0-based) and
    a[:k] <= a[k] <= a[k+1:]. Returns a[k]."""
    lo, hi = 0, len(a) - 1
    while True:
        p = _partition(a, lo, hi)
        if p == k:
            return a[k]
        if p < k:
            lo = p + 1
        else:
            hi = p - 1


def kth_largest(nums, k):
    """k is 1-based. Copies the input."""
    a = list(nums)
    return quickselect(a, len(a) - k)


def k_smallest(nums, k):
    """The k smallest values, any order. O(n) expected."""
    if k == 0:
        return []
    a = list(nums)
    quickselect(a, k - 1)
    return a[:k]


def median_of_medians(a, k):
    """k-th smallest (0-based) in O(n) WORST case. Not in place, for clarity."""
    if len(a) <= 5:
        return sorted(a)[k]
    medians = [sorted(a[i:i + 5])[len(a[i:i + 5]) // 2] for i in range(0, len(a), 5)]
    pivot = median_of_medians(medians, len(medians) // 2)
    lows = [x for x in a if x < pivot]
    highs = [x for x in a if x > pivot]
    equal = len(a) - len(lows) - len(highs)
    if k < len(lows):
        return median_of_medians(lows, k)
    if k < len(lows) + equal:
        return pivot
    return median_of_medians(highs, k - len(lows) - equal)


def wiggle_sort(nums):
    """Wiggle sort II: nums[0] < nums[1] > nums[2] < ... in place.

    Find the median, then put the smaller half on even slots and the larger
    half on odd slots, each in REVERSE so copies of the median sit far apart.
    O(n) expected time; this version uses O(n) extra space for clarity.
    """
    n = len(nums)
    if n < 2:
        return nums
    a = list(nums)
    mid = quickselect(a, (n - 1) // 2)
    small = [x for x in a if x < mid]
    big = [x for x in a if x > mid]
    eq = [mid] * (n - len(small) - len(big))
    order = small + eq + big            # three-way split around the median
    half = (n + 1) // 2
    nums[::2] = order[:half][::-1]      # reversed: medians go to the ends
    nums[1::2] = order[half:][::-1]
    return nums


# ------------------------------------------------------------------------ tests


def test_kth_largest_examples():
    assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
    assert kth_largest([7], 1) == 7


def test_quickselect_matches_sorted_and_partitions():
    random.seed(21)
    for _ in range(300):
        a = [random.randint(-20, 20) for _ in range(random.randint(1, 30))]
        k = random.randrange(len(a))
        b = list(a)
        assert quickselect(b, k) == sorted(a)[k]
        assert sorted(b) == sorted(a)              # a permutation
        assert all(x <= b[k] for x in b[:k])
        assert all(x >= b[k] for x in b[k + 1:])


def test_kth_largest_does_not_mutate():
    a = [5, 1, 4]
    kth_largest(a, 1)
    assert a == [5, 1, 4]


def test_k_smallest_as_multiset():
    random.seed(22)
    for _ in range(200):
        a = [random.randint(-9, 9) for _ in range(random.randint(0, 25))]
        k = random.randint(0, len(a))
        assert sorted(k_smallest(a, k)) == sorted(a)[:k]


def test_median_of_medians_matches_sorted():
    random.seed(23)
    for _ in range(200):
        a = [random.randint(-30, 30) for _ in range(random.randint(1, 80))]
        k = random.randrange(len(a))
        assert median_of_medians(a, k) == sorted(a)[k]
    assert median_of_medians(list(range(1000)), 500) == 500


def _is_wiggle(a):
    return all((a[i] < a[i + 1]) if i % 2 == 0 else (a[i] > a[i + 1])
               for i in range(len(a) - 1))


def test_wiggle_sort():
    assert _is_wiggle(wiggle_sort([1, 5, 1, 1, 6, 4]))
    assert _is_wiggle(wiggle_sort([4, 5, 5, 6]))     # naive split fails this
    assert wiggle_sort([]) == []
    assert wiggle_sort([3]) == [3]
    random.seed(24)
    for _ in range(300):
        a = [random.randint(0, 4) for _ in range(random.randint(1, 7))]
        exists = any(_is_wiggle(p) for p in permutations(a))   # brute force
        got = wiggle_sort(list(a))
        assert sorted(got) == sorted(a)
        assert _is_wiggle(got) == exists   # succeeds whenever any answer exists


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
