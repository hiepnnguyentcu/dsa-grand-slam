"""Monotonic deque — the max or min of a sliding window in O(1) amortised.

Signs: "maximum of every window of size k", "longest subarray where max - min
       <= limit", "shortest subarray with sum >= k" when values can be negative.
Approach: keep a deque of candidates in monotonic order. New items evict
          worse ones from the back (they can never be the answer while the new
          one is in the window); items that leave the window are popped from
          the front. The front is always the current best.
Complexity: O(n) — every index enters and leaves the deque once.
Gotchas:
  - Store indices, not values, when you need to know whether the front has
    left the window. Values work only if you pop by comparing to a[left].
  - Max deque pops on `<`, keeping equal values; popping on `<=` is fine too,
    but then the left-side check must use indices.
  - Shortest sum >= k with negatives: sliding window two-pointer is wrong, a
    deque over prefix sums is right.
  - A DP whose transition is max over the last k states is the same trick:
    see dynamic_programming/deque_optimization.py.

Run the tests at the bottom with:  python3 stacks_heaps/monotonic_deque.py
"""

from collections import deque


# ---------------------------------------------------------------- implementation


def max_sliding_window(a, k):
    """LC 239. Max of each window a[i-k+1..i]."""
    dq, out = deque(), []  # indices, values decreasing front to back
    for i, x in enumerate(a):
        while dq and a[dq[-1]] < x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:  # front has slid out of the window
            dq.popleft()
        if i >= k - 1:
            out.append(a[dq[0]])
    return out


def longest_subarray_within_limit(a, limit):
    """LC 1438. Longest window with max - min <= limit. Two deques."""
    hi, lo = deque(), deque()  # values: hi non-increasing, lo non-decreasing
    left = best = 0
    for right, x in enumerate(a):
        while hi and hi[-1] < x:
            hi.pop()
        hi.append(x)
        while lo and lo[-1] > x:
            lo.pop()
        lo.append(x)
        while hi[0] - lo[0] > limit:
            if hi[0] == a[left]:  # by value: equal copies were kept, so safe
                hi.popleft()
            if lo[0] == a[left]:
                lo.popleft()
            left += 1
        best = max(best, right - left + 1)
    return best


def shortest_subarray_at_least(a, k):
    """LC 862. Shortest non-empty subarray with sum >= k, or -1. Negatives allowed.

    Deque of prefix indices with increasing prefix sums. A front index that
    already works is popped: any later end would only give a longer answer.
    A back index with prefix >= the new one is useless: the new one is both
    later and smaller.
    """
    p = [0]
    for x in a:
        p.append(p[-1] + x)
    best, dq = len(a) + 1, deque()
    for j in range(len(p)):
        while dq and p[j] - p[dq[0]] >= k:
            best = min(best, j - dq.popleft())
        while dq and p[dq[-1]] >= p[j]:
            dq.pop()
        dq.append(j)
    return best if best <= len(a) else -1


# ------------------------------------------------------------------------ tests


def test_sliding_window_example():
    assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert max_sliding_window([4], 1) == [4]


def test_sliding_window_matches_brute_force():
    import random

    rng = random.Random(21)
    for _ in range(300):
        n = rng.randint(1, 30)
        a = [rng.randint(-5, 5) for _ in range(n)]  # small range: many ties
        k = rng.randint(1, n)
        assert max_sliding_window(a, k) == [max(a[i:i + k]) for i in range(n - k + 1)]


def test_limit_example():
    assert longest_subarray_within_limit([8, 2, 4, 7], 4) == 2
    assert longest_subarray_within_limit([10, 1, 2, 4, 7, 2], 5) == 4
    assert longest_subarray_within_limit([4, 2, 2, 2, 4, 4, 2, 2], 0) == 3


def test_limit_matches_brute_force():
    import random

    rng = random.Random(22)
    for _ in range(300):
        a = [rng.randint(0, 9) for _ in range(rng.randint(1, 25))]
        limit = rng.randint(0, 6)
        brute = max(
            j - i + 1
            for i in range(len(a))
            for j in range(i, len(a))
            if max(a[i:j + 1]) - min(a[i:j + 1]) <= limit
        )
        assert longest_subarray_within_limit(a, limit) == brute


def test_shortest_at_least_example():
    assert shortest_subarray_at_least([1], 1) == 1
    assert shortest_subarray_at_least([1, 2], 4) == -1
    assert shortest_subarray_at_least([2, -1, 2], 3) == 3
    assert shortest_subarray_at_least([84, -37, 32, 40, 95], 167) == 3


def test_shortest_at_least_matches_brute_force():
    import random

    rng = random.Random(23)
    for _ in range(400):
        a = [rng.randint(-6, 8) for _ in range(rng.randint(1, 20))]
        k = rng.randint(-3, 20)
        lengths = [
            j - i
            for i in range(len(a))
            for j in range(i + 1, len(a) + 1)
            if sum(a[i:j]) >= k
        ]
        assert shortest_subarray_at_least(a, k) == (min(lengths) if lengths else -1)


def test_deque_is_linear():
    a = list(range(200_000, 0, -1))  # decreasing: deque grows to k then slides
    assert len(max_sliding_window(a, 1000)) == len(a) - 999


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
