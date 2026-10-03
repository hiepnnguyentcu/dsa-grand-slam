"""Monotonic stack — nearest greater / smaller element on each side.

Signs: "next greater element", "how many days until warmer", "span of days
       with price <= today", "for each element, how far does it reach",
       sum over all subarrays of their min or max.
Approach: scan once, keeping a stack of indices whose values are monotonic
          (decreasing for next-greater). A new value pops everything it beats
          — and for each popped index, the new value *is* its answer. What
          stays on the stack is still waiting.
Complexity: O(n) time — each index is pushed once and popped at most once.
            O(n) space.
Gotchas:
  - Store indices, not values: distances and widths need positions.
  - Strict vs non-strict comparison decides how ties behave. For
    "sum of subarray minimums", use < on one side and <= on the other, or
    equal values double-count.
  - Circular arrays: walk 0..2n-1 and index with i % n; push only in the
    first pass.
  - Decreasing stack -> answers "next greater"; increasing -> "next smaller".

Run the tests at the bottom with:  python3 stacks_heaps/monotonic_stack.py
"""

MOD = 10**9 + 7


# ---------------------------------------------------------------- implementation


def next_greater(nums):
    """For each i, the next value strictly greater than nums[i], or -1."""
    ans = [-1] * len(nums)
    stack = []  # indices; their values are decreasing bottom -> top
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            ans[stack.pop()] = x
        stack.append(i)
    return ans


def next_greater_circular(nums):
    """As next_greater, but the array wraps around."""
    n = len(nums)
    ans = [-1] * n
    stack = []
    for i in range(2 * n):
        x = nums[i % n]
        while stack and nums[stack[-1]] < x:
            ans[stack.pop()] = x
        if i < n:
            stack.append(i)
    return ans


def next_smaller_index(nums):
    """For each i, the index of the next strictly smaller value, or n."""
    n = len(nums)
    ans = [n] * n
    stack = []  # increasing
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] > x:
            ans[stack.pop()] = i
        stack.append(i)
    return ans


def daily_temperatures(temps):
    """Days to wait for a strictly warmer day, 0 if never."""
    ans = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans


class StockSpanner:
    """Online: span = consecutive days up to today with price <= today's.

    Each stack entry carries the span it absorbed, so popped days are never
    looked at again.
    """

    def __init__(self):
        self.stack = []  # (price, span), prices strictly decreasing

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append((price, span))
        return span


def sum_subarray_mins(arr):
    """Sum of min(sub) over every contiguous subarray, mod 1e9+7.

    arr[i] is the min of every subarray that starts after its previous
    smaller-or-equal element and ends before its next strictly smaller one:
    (i - left) * (right - i) subarrays. The asymmetric tie rule gives each
    subarray exactly one owner.
    """
    n = len(arr)
    left = [-1] * n   # previous index with value <= arr[i]
    right = [n] * n   # next index with value < arr[i]
    stack = []
    for i, x in enumerate(arr):
        while stack and arr[stack[-1]] > x:
            right[stack.pop()] = i
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    return sum(arr[i] * (i - left[i]) * (right[i] - i) for i in range(n)) % MOD


def sum_subarray_ranges(nums):
    """Sum of (max - min) over every subarray = sum of maxes - sum of mins."""

    def sum_of(sign):
        a = [sign * x for x in nums]
        n = len(a)
        total = 0
        stack = []
        for i in range(n + 1):
            while stack and (i == n or a[stack[-1]] > a[i]):
                j = stack.pop()
                left = stack[-1] if stack else -1
                total += a[j] * (j - left) * (i - j)
            stack.append(i)
        return total

    return -sum_of(-1) - sum_of(1)


# ------------------------------------------------------------------------ tests


def random_arrays(count, max_len, hi, seed):
    import random

    rng = random.Random(seed)
    for _ in range(count):
        yield [rng.randint(0, hi) for _ in range(rng.randint(0, max_len))]


def brute_next_greater(nums, circular=False):
    n = len(nums)
    out = []
    for i in range(n):
        js = range(i + 1, i + n) if circular else range(i + 1, n)
        out.append(next((nums[j % n] for j in js if nums[j % n] > nums[i]), -1))
    return out


def test_next_greater_examples():
    assert next_greater([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
    assert next_greater_circular([1, 2, 1]) == [2, -1, 2]
    assert next_greater([]) == []


def test_next_greater_matches_brute_force():
    for a in random_arrays(800, 12, 6, seed=1):  # small range -> many ties
        assert next_greater(a) == brute_next_greater(a)
        assert next_greater_circular(a) == brute_next_greater(a, circular=True)


def test_next_smaller_index_matches_brute_force():
    for a in random_arrays(800, 12, 6, seed=2):
        n = len(a)
        expect = [next((j for j in range(i + 1, n) if a[j] < a[i]), n) for i in range(n)]
        assert next_smaller_index(a) == expect


def test_daily_temperatures():
    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
    for a in random_arrays(800, 12, 6, seed=3):
        n = len(a)
        expect = [next((j - i for j in range(i + 1, n) if a[j] > a[i]), 0) for i in range(n)]
        assert daily_temperatures(a) == expect


def test_stock_spanner():
    s = StockSpanner()
    assert [s.next(p) for p in [100, 80, 60, 70, 60, 75, 85]] == [1, 1, 1, 2, 1, 4, 6]
    for a in random_arrays(500, 15, 6, seed=4):
        s = StockSpanner()
        for i, p in enumerate(a):
            k = i
            while k >= 0 and a[k] <= p:
                k -= 1
            assert s.next(p) == i - k


def test_sum_subarray_mins():
    assert sum_subarray_mins([3, 1, 2, 4]) == 17
    assert sum_subarray_mins([11, 81, 94, 43, 3]) == 444
    for a in random_arrays(600, 10, 5, seed=5):  # ties are the risky case
        brute = sum(min(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1))
        assert sum_subarray_mins(a) == brute % MOD, a


def test_sum_subarray_ranges():
    assert sum_subarray_ranges([1, 2, 3]) == 4
    assert sum_subarray_ranges([4, -2, -3, 4, 1]) == 59
    for a in random_arrays(600, 10, 5, seed=6):
        brute = sum(
            max(a[i:j]) - min(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1)
        )
        assert sum_subarray_ranges(a) == brute, a


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
