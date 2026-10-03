"""Top-k — keep the k best with a heap of size k.

Signs: "k largest/smallest", "kth largest", "k most frequent", "k closest",
       a stream where you report the kth largest after every insert.
Approach: to keep the k *largest*, use a *min*-heap of size k: its root is
          the weakest of the current top k, so a new item only gets in if it
          beats the root. (Flip everything for k smallest.) Quickselect finds
          the kth element in expected O(n) when the data is all in memory.
          Bucket sort by frequency gives top-k-frequent in O(n).
Complexity: heap O(n log k) time, O(k) space. Quickselect O(n) expected,
            O(n^2) worst. Bucket O(n).
Gotchas:
  - The heap type is the *opposite* of what you keep: k largest -> min-heap.
  - heapreplace (pop then push) is one sift instead of two; use it once the
    heap is full.
  - Quickselect: pick a random pivot and use three-way partition, or sorted
    and all-equal inputs go quadratic.
  - Ties in "top k frequent" are usually unordered — compare as sets.

Run the tests at the bottom with:  python3 stacks_heaps/top_k.py
"""

import heapq
import random
from collections import Counter


# ---------------------------------------------------------------- implementation


def kth_largest(nums, k):
    """kth largest value (1-based), by a size-k min-heap."""
    h = []
    for x in nums:
        if len(h) < k:
            heapq.heappush(h, x)
        elif x > h[0]:
            heapq.heapreplace(h, x)
    return h[0]


def kth_largest_quickselect(nums, k):
    """kth largest value in expected O(n): partition around a random pivot."""
    a = list(nums)
    target = len(a) - k  # index in ascending order
    lo, hi = 0, len(a) - 1
    while True:
        pivot = a[random.randint(lo, hi)]
        # three-way partition of a[lo..hi] into < pivot | == pivot | > pivot
        lt, i, gt = lo, lo, hi
        while i <= gt:
            if a[i] < pivot:
                a[lt], a[i] = a[i], a[lt]
                lt += 1
                i += 1
            elif a[i] > pivot:
                a[gt], a[i] = a[i], a[gt]
                gt -= 1
            else:
                i += 1
        if target < lt:
            hi = lt - 1
        elif target > gt:
            lo = gt + 1
        else:
            return pivot


class KthLargest:
    """Stream: add(x) returns the kth largest seen so far."""

    def __init__(self, k, nums):
        self.k = k
        self.h = []
        for x in nums:
            self.add(x)

    def add(self, x):
        if len(self.h) < self.k:
            heapq.heappush(self.h, x)
        elif x > self.h[0]:
            heapq.heapreplace(self.h, x)
        return self.h[0] if len(self.h) == self.k else None


def top_k_frequent(nums, k):
    """k most frequent values, by a size-k min-heap on (count, value)."""
    h = []
    for x, c in Counter(nums).items():
        heapq.heappush(h, (c, x))
        if len(h) > k:
            heapq.heappop(h)
    return [x for _, x in h]


def top_k_frequent_bucket(nums, k):
    """Same answer in O(n): bucket i holds the values seen exactly i times."""
    buckets = [[] for _ in range(len(nums) + 1)]
    for x, c in Counter(nums).items():
        buckets[c].append(x)
    out = []
    for c in range(len(nums), 0, -1):
        for x in buckets[c]:
            out.append(x)
            if len(out) == k:
                return out
    return out


def k_closest(points, k):
    """k points closest to the origin: a max-heap of size k on distance."""
    h = []  # (-dist^2, x, y): the root is the farthest of the kept ones
    for x, y in points:
        d = x * x + y * y
        if len(h) < k:
            heapq.heappush(h, (-d, x, y))
        elif d < -h[0][0]:
            heapq.heapreplace(h, (-d, x, y))
    return [(x, y) for _, x, y in h]


# ------------------------------------------------------------------------ tests


def test_kth_largest_examples():
    assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
    assert kth_largest_quickselect([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
    assert kth_largest_quickselect([7] * 50, 25) == 7  # all equal: three-way


def test_kth_largest_matches_sorting():
    rng = random.Random(1)
    random.seed(1)  # quickselect's pivots
    for _ in range(1000):
        nums = [rng.randint(-10, 10) for _ in range(rng.randint(1, 20))]
        k = rng.randint(1, len(nums))
        expect = sorted(nums, reverse=True)[k - 1]
        assert kth_largest(nums, k) == expect
        assert kth_largest_quickselect(nums, k) == expect


def test_kth_largest_stream():
    s = KthLargest(3, [4, 5, 8, 2])
    assert [s.add(x) for x in [3, 5, 10, 9, 4]] == [4, 5, 5, 8, 8]
    rng = random.Random(2)
    for _ in range(100):
        k = rng.randint(1, 5)
        seen = [rng.randint(0, 20) for _ in range(rng.randint(0, 6))]
        s = KthLargest(k, seen)
        for _ in range(20):
            x = rng.randint(0, 20)
            seen.append(x)
            expect = sorted(seen, reverse=True)[k - 1] if len(seen) >= k else None
            assert s.add(x) == expect


def test_top_k_frequent():
    assert set(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == {1, 2}
    rng = random.Random(3)
    for _ in range(500):
        nums = [rng.randint(0, 6) for _ in range(rng.randint(1, 25))]
        cnt = Counter(nums)
        k = rng.randint(1, len(cnt))
        for got in (top_k_frequent(nums, k), top_k_frequent_bucket(nums, k)):
            assert len(set(got)) == k
            # valid iff no excluded value is strictly more frequent than an included one
            worst_in = min(cnt[x] for x in got)
            best_out = max((c for x, c in cnt.items() if x not in got), default=0)
            assert worst_in >= best_out
            assert sorted((cnt[x] for x in got), reverse=True) == sorted(cnt.values(), reverse=True)[:k]


def test_k_closest():
    assert sorted(k_closest([(1, 3), (-2, 2)], 1)) == [(-2, 2)]
    rng = random.Random(4)
    for _ in range(500):
        pts = [(rng.randint(-5, 5), rng.randint(-5, 5)) for _ in range(rng.randint(1, 15))]
        k = rng.randint(1, len(pts))
        got = k_closest(pts, k)
        dist = lambda p: p[0] ** 2 + p[1] ** 2
        assert sorted(map(dist, got)) == sorted(map(dist, pts))[:k]
        assert Counter(got) <= Counter(pts)  # only real points, each used once


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
