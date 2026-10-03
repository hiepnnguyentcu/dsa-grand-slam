"""Merge-sort counting — count cross pairs (i < j) during the merge.

Signs: "count pairs i < j with nums[i] > nums[j]" (inversions), "count of
       smaller numbers after self", reverse pairs (nums[i] > 2 * nums[j]),
       count of range sum (lower <= p[j] - p[i] <= upper), n up to 1e5 so
       O(n^2) is out.
Approach: in merge sort, every pair (i, j) with i < j is split exactly once:
          i in the left half, j in the right. At that moment both halves are
          sorted, so a two-pointer sweep counts all cross pairs in linear time.
          Then merge as usual. Count first, merge second when the condition
          differs from plain `<` (reverse pairs, range sums).
          Fenwick alternative (compress values, scan right to left):
          prefix_sums/fenwick.py.
Complexity: O(n log n) time, O(n) extra.
Gotchas:
  - Per-index answers (smaller after self): sort INDICES by value so you know
    whose counter to bump. When a left item is placed, add how many right
    items were placed before it.
  - Ties: "smaller" means strictly; take left first on equal values so equal
    right items are not counted.
  - Reverse pairs: 2 * nums[j] — fine in Python, overflows int32 elsewhere.
  - Range sum: run it on the prefix array (length n + 1), not on nums.

Run the tests at the bottom with:  python3 sorting/merge_count.py
"""

import random


# ---------------------------------------------------------------- implementation


def count_inversions(a):
    """Pairs i < j with a[i] > a[j]."""

    def sort(lo, hi):                     # sorts arr[lo:hi], returns inversions
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        inv = sort(lo, mid) + sort(mid, hi)
        merged, i, j = [], lo, mid
        while i < mid and j < hi:
            if arr[i] <= arr[j]:
                merged.append(arr[i])
                i += 1
            else:                         # arr[j] beats every arr[i..mid-1]
                inv += mid - i
                merged.append(arr[j])
                j += 1
        merged += arr[i:mid] + arr[j:hi]
        arr[lo:hi] = merged
        return inv

    arr = list(a)
    return sort(0, len(arr))


def count_smaller_after_self(nums):
    """out[i] = #{j > i : nums[j] < nums[i]}. Merge sort over indices."""
    n = len(nums)
    out = [0] * n
    idx = list(range(n))

    def sort(lo, hi):
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        sort(lo, mid)
        sort(mid, hi)
        merged, i, j = [], lo, mid
        while i < mid or j < hi:
            if j == hi or (i < mid and nums[idx[i]] <= nums[idx[j]]):
                out[idx[i]] += j - mid        # right items already placed are smaller
                merged.append(idx[i])
                i += 1
            else:
                merged.append(idx[j])
                j += 1
        idx[lo:hi] = merged

    sort(0, n)
    return out


def reverse_pairs(nums):
    """Pairs i < j with nums[i] > 2 * nums[j]. Count with two pointers, then merge."""

    def sort(lo, hi):
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        cnt = sort(lo, mid) + sort(mid, hi)
        j = mid
        for i in range(lo, mid):              # left is sorted: j only moves right
            while j < hi and arr[i] > 2 * arr[j]:
                j += 1
            cnt += j - mid
        arr[lo:hi] = sorted(arr[lo:hi])       # or a linear merge; same big-O here
        return cnt

    arr = list(nums)
    return sort(0, len(arr))


def count_range_sum(nums, lower, upper):
    """Subarrays with lower <= sum <= upper.

    Sum(i..j-1) = p[j] - p[i]. For each right-half j, count left-half i with
    p[j] - upper <= p[i] <= p[j] - lower. Both pointers only move forward.
    """
    p = [0]
    for x in nums:
        p.append(p[-1] + x)

    def sort(lo, hi):
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        cnt = sort(lo, mid) + sort(mid, hi)
        a = b = lo                           # window [a, b) in the left half
        for j in range(mid, hi):
            while a < mid and p[a] < p[j] - upper:
                a += 1
            while b < mid and p[b] <= p[j] - lower:
                b += 1
            cnt += b - a
        p[lo:hi] = sorted(p[lo:hi])
        return cnt

    return sort(0, len(p))


# ------------------------------------------------------------------------ tests


def _rand_lists(seed, count=200, lo=-10, hi=10, max_n=30):
    random.seed(seed)
    yield []
    yield [1]
    yield [2, 2, 2]
    for _ in range(count):
        yield [random.randint(lo, hi) for _ in range(random.randint(0, max_n))]


def test_inversions_examples():
    assert count_inversions([2, 4, 1, 3, 5]) == 3
    assert count_inversions(list(range(10))) == 0
    assert count_inversions(list(range(10, 0, -1))) == 45


def test_inversions_match_brute_force():
    for a in _rand_lists(31):
        brute = sum(a[i] > a[j] for i in range(len(a)) for j in range(i + 1, len(a)))
        assert count_inversions(a) == brute


def test_count_smaller_matches_brute_force():
    assert count_smaller_after_self([5, 2, 6, 1]) == [2, 1, 1, 0]
    for a in _rand_lists(32):
        brute = [sum(a[j] < a[i] for j in range(i + 1, len(a))) for i in range(len(a))]
        assert count_smaller_after_self(a) == brute


def test_reverse_pairs_match_brute_force():
    assert reverse_pairs([1, 3, 2, 3, 1]) == 2
    assert reverse_pairs([2, 4, 3, 5, 1]) == 3
    for a in _rand_lists(33):
        brute = sum(a[i] > 2 * a[j] for i in range(len(a)) for j in range(i + 1, len(a)))
        assert reverse_pairs(a) == brute


def test_count_range_sum_matches_brute_force():
    assert count_range_sum([-2, 5, -1], -2, 2) == 3
    random.seed(34)
    for a in _rand_lists(35):
        lo = random.randint(-15, 10)
        hi = lo + random.randint(0, 15)
        brute = sum(lo <= sum(a[i:j]) <= hi
                    for i in range(len(a)) for j in range(i + 1, len(a) + 1))
        assert count_range_sum(a, lo, hi) == brute


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
