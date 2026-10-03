"""Two heaps — a max-heap and a min-heap facing each other.

Signs: "median of a data stream", a value that splits the data into a lower
       and an upper half, "pick the best option among those currently
       affordable" (IPO / maximise capital).
Approach:
  - Median: `lo` is a max-heap of the smaller half, `hi` a min-heap of the
    larger half. Keep every lo <= every hi and len(lo) == len(hi) or
    len(hi) + 1. The median is lo's top, or the mean of both tops.
  - Affordable-best (IPO): a min-heap of locked options keyed by cost, a
    max-heap of unlocked options keyed by value. As budget grows, move
    everything now affordable across, then take the best unlocked one.
Complexity: median add O(log n), query O(1). IPO O(n log n).
Gotchas:
  - Insert by routing through the other heap (push to lo, move lo's top to
    hi, rebalance). That keeps the order invariant without comparisons.
  - Python's lo stores negatives — negate on every read.
  - Mean of two ints: return a float (or use / 2), not //.
  - IPO: if nothing is affordable, stop early — capital can't grow.

Run the tests at the bottom with:  python3 stacks_heaps/two_heaps.py
"""

import heapq


# ---------------------------------------------------------------- implementation


class MedianFinder:
    def __init__(self):
        self.lo = []  # max-heap via negation: the smaller half
        self.hi = []  # min-heap: the larger half

    def add(self, x):
        heapq.heappush(self.lo, -x)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))  # largest of lo moves up
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def median(self):
        if len(self.lo) > len(self.hi):
            return float(-self.lo[0])
        return (-self.lo[0] + self.hi[0]) / 2


def find_maximized_capital(k, w, profits, capital):
    """Final capital after at most k projects (LeetCode 502, IPO).

    Each project needs capital[i] to start and adds profits[i] when done.
    """
    locked = sorted(zip(capital, profits))  # by cost; a sorted list works as the min-heap
    unlocked = []  # max-heap of profits
    i = 0
    for _ in range(k):
        while i < len(locked) and locked[i][0] <= w:
            heapq.heappush(unlocked, -locked[i][1])
            i += 1
        if not unlocked:
            break
        w -= heapq.heappop(unlocked)
    return w


# ------------------------------------------------------------------------ tests


def test_median_example():
    m = MedianFinder()
    m.add(1)
    m.add(2)
    assert m.median() == 1.5
    m.add(3)
    assert m.median() == 2.0


def test_median_matches_sorting():
    import random
    from statistics import median

    rng = random.Random(1)
    for _ in range(50):
        m, seen = MedianFinder(), []
        for _ in range(60):
            x = rng.randint(-20, 20)
            m.add(x)
            seen.append(x)
            assert m.median() == median(seen)
            assert len(m.lo) - len(m.hi) in (0, 1)
            assert not m.hi or -m.lo[0] <= m.hi[0]


def brute_capital(k, w, profits, capital):
    """Try every order of up to k distinct projects."""
    from itertools import permutations

    best = w
    n = len(profits)
    for r in range(1, min(k, n) + 1):
        for order in permutations(range(n), r):
            cur = w
            for i in order:
                if capital[i] > cur:
                    break
                cur += profits[i]
            else:
                best = max(best, cur)
    return best


def test_ipo():
    import random

    assert find_maximized_capital(2, 0, [1, 2, 3], [0, 1, 1]) == 4
    assert find_maximized_capital(3, 0, [1, 2, 3], [0, 1, 2]) == 6
    assert find_maximized_capital(1, 0, [5], [1]) == 0  # nothing affordable
    rng = random.Random(2)
    for _ in range(300):
        n = rng.randint(1, 5)
        profits = [rng.randint(0, 5) for _ in range(n)]
        capital = [rng.randint(0, 8) for _ in range(n)]
        k, w = rng.randint(1, n), rng.randint(0, 4)
        assert find_maximized_capital(k, w, profits, capital) == brute_capital(k, w, profits, capital)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
