"""Lazy deletion — remove from a heap by marking, clean up only at the top.

Signs: a heap where items must leave *before* they reach the top — a sliding
       window leaving behind old values, a record whose value gets corrected
       ("stock price fluctuation"), cancelled tasks.
Approach: heapq cannot delete from the middle. Instead, record the removal
          (a counter of pending deletions, or a version stamp per key) and,
          whenever you read the top, pop while the top is marked dead. The
          heap may hold garbage, but never at the root after a prune.
Complexity: each item is pushed once and popped once, so O(log n) amortised
            per operation. Space can grow to every item ever pushed.
Gotchas:
  - Keep a separate count of *live* items; len(heap) includes the dead ones.
  - Two heaps (sliding median): balance by live sizes, and prune both tops
    after every move — a dead item must never be moved between heaps.
  - Version stamps: store (value, key, version) and compare with the latest
    version for that key; the value alone is ambiguous when it repeats.

Run the tests at the bottom with:  python3 stacks_heaps/lazy_deletion.py
"""

import heapq
from collections import Counter


# ---------------------------------------------------------------- implementation


class LazyHeap:
    """Min-heap with remove(x) for any x currently in it."""

    def __init__(self):
        self.h = []
        self.dead = Counter()  # value -> deletions not yet popped
        self.size = 0          # live items

    def push(self, x):
        heapq.heappush(self.h, x)
        self.size += 1

    def remove(self, x):
        self.dead[x] += 1
        self.size -= 1
        self._prune()

    def _prune(self):
        while self.h and self.dead[self.h[0]]:
            self.dead[self.h[0]] -= 1
            heapq.heappop(self.h)

    def top(self):
        self._prune()
        return self.h[0]

    def pop(self):
        self._prune()
        self.size -= 1
        x = heapq.heappop(self.h)
        self._prune()
        return x

    def __len__(self):
        return self.size


def sliding_window_median(nums, k):
    """Median of each length-k window, as floats.

    lo = max-heap (negated) of the smaller half, hi = min-heap of the larger.
    Invariant after each step: live sizes are len(lo) == len(hi) or one more.
    """
    lo, hi = LazyHeap(), LazyHeap()

    def rebalance():
        while len(lo) > len(hi) + 1:  # a push plus a removal can skew it by 3
            hi.push(-lo.pop())
        while len(hi) > len(lo):
            lo.push(-hi.pop())

    def median():
        if k % 2:
            return float(-lo.top())
        return (-lo.top() + hi.top()) / 2

    out = []
    for i, x in enumerate(nums):
        if not len(lo) or x <= -lo.top():
            lo.push(-x)
        else:
            hi.push(x)
        if i >= k:
            old = nums[i - k]
            if old <= -lo.top():  # <= lo's max: a copy of it is in lo
                lo.remove(-old)
            else:
                hi.remove(old)
        rebalance()
        if i >= k - 1:
            out.append(median())
    return out


class StockPrice:
    """Out-of-order price updates; corrections overwrite.

    Heaps hold (price, timestamp) for every update ever seen. An entry is
    stale if its timestamp's current price differs; prune stale tops on read.
    """

    def __init__(self):
        self.price = {}
        self.latest = 0
        self.min_h, self.max_h = [], []

    def update(self, t, p):
        self.price[t] = p
        self.latest = max(self.latest, t)
        heapq.heappush(self.min_h, (p, t))
        heapq.heappush(self.max_h, (-p, t))

    def current(self):
        return self.price[self.latest]

    def maximum(self):
        while self.price[self.max_h[0][1]] != -self.max_h[0][0]:
            heapq.heappop(self.max_h)
        return -self.max_h[0][0]

    def minimum(self):
        while self.price[self.min_h[0][1]] != self.min_h[0][0]:
            heapq.heappop(self.min_h)
        return self.min_h[0][0]


# ------------------------------------------------------------------------ tests


def test_lazy_heap_matches_list():
    import random

    rng = random.Random(1)
    h, ref = LazyHeap(), []
    for _ in range(5000):
        r = rng.random()
        if ref and r < 0.25:
            x = rng.choice(ref)  # delete from the middle
            ref.remove(x)
            h.remove(x)
        elif ref and r < 0.4:
            assert h.pop() == min(ref)
            ref.remove(min(ref))
        else:
            x = rng.randint(0, 10)
            h.push(x)
            ref.append(x)
        assert len(h) == len(ref)
        if ref:
            assert h.top() == min(ref)


def test_sliding_window_median_example():
    got = sliding_window_median([1, 3, -1, -3, 5, 3, 6, 7], 3)
    assert got == [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]
    assert sliding_window_median([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]


def test_sliding_window_median_matches_sorting():
    import random
    from statistics import median

    rng = random.Random(2)
    for _ in range(400):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(1, 20))]  # many duplicates
        k = rng.randint(1, len(nums))
        expect = [float(median(nums[i : i + k])) for i in range(len(nums) - k + 1)]
        assert sliding_window_median(nums, k) == expect, (nums, k)


def test_stock_price():
    import random

    s = StockPrice()
    s.update(1, 10)
    s.update(2, 5)
    assert s.current() == 5 and s.maximum() == 10
    s.update(1, 3)  # correction: timestamp 1 was really 3
    assert s.maximum() == 5 and s.minimum() == 3
    s.update(4, 2)
    assert s.minimum() == 2 and s.current() == 2

    rng = random.Random(3)
    for _ in range(100):
        s, ref = StockPrice(), {}
        for _ in range(40):
            t, p = rng.randint(1, 8), rng.randint(1, 10)
            s.update(t, p)
            ref[t] = p
            assert s.current() == ref[max(ref)]
            assert s.maximum() == max(ref.values())
            assert s.minimum() == min(ref.values())


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
