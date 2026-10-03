"""Real-valued binary search — integer sqrt, roots to a precision, fractional answers.

Signs: "sqrt without a library", "answer within 1e-5", an answer that is a
       real number (average, ratio, distance), a continuous monotone function.
Approach:
  - Integer version: largest x with x * x <= n is last_true on integers.
  - Real version: keep lo < answer <= hi and halve. There is no "mid + 1",
    so stop on a fixed iteration count (100 halvings shrinks any double
    range below its precision) or when hi - lo < eps.
  - Fractional answers (max average): binary search the value v, and turn
    "is there a window with average >= v?" into "is there a window whose
    sum of (a[i] - v) is >= 0?" — a prefix-sum check.
Complexity: O(log(range / eps)) checks, i.e. O(iterations x check).
Gotchas:
  - `while hi - lo > eps` can spin forever when eps is below the float
    spacing near the answer. Fixed iterations always terminate.
  - Integer sqrt: hi = n // 2 + 1 misses n = 1 (1 * 1 is not > 1); use + 2. x * x can't overflow
    in Python, but use x <= n // x in C/Java.
  - Negative cube roots: start the bracket at [min(n, -1), max(n, 1)], not
    [0, n]. For |n| < 1 the root is larger in magnitude than n.
  - Compare floats with a tolerance in tests; the search returns an interval.

Run the tests at the bottom with:  python3 binary_search/real_valued.py
"""


# ---------------------------------------------------------------- implementation


def isqrt(n):
    """floor(sqrt(n)) for n >= 0: the largest x with x * x <= n."""
    lo, hi = 0, n // 2 + 2        # hi * hi > n for every n >= 0 (n // 2 + 1 fails at n = 1)
    while lo < hi:                # first x with x * x > n, then step back
        mid = (lo + hi) // 2
        if mid * mid > n:
            hi = mid
        else:
            lo = mid + 1
    return lo - 1


def sqrt_real(x, iterations=100):
    """sqrt(x) for x >= 0 by bisection. Bracket [0, max(1, x)] holds the root."""
    lo, hi = 0.0, max(1.0, x)
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if mid * mid < x:
            lo = mid
        else:
            hi = mid
    return hi


def cbrt_real(x, iterations=200):
    """Real cube root, negatives included. t ** 3 is increasing everywhere."""
    lo, hi = min(x, -1.0), max(x, 1.0)
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if mid ** 3 < x:
            lo = mid
        else:
            hi = mid
    return hi


def max_average_at_least_k(nums, k, iterations=60):
    """Largest average of any contiguous subarray of length >= k.

    has(v): subtract v from every element; a window with average >= v is a
    window with non-negative sum. Track the best prefix minimum seen at least
    k positions back. has() is True ... True False ... False in v.
    """
    def has(v):
        prefix = [0.0]
        for a in nums:
            prefix.append(prefix[-1] + a - v)
        best_min = float("inf")
        for j in range(k, len(nums) + 1):
            best_min = min(best_min, prefix[j - k])
            if prefix[j] - best_min >= 0:
                return True
        return False

    lo, hi = min(nums), max(nums)
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if has(mid):
            lo = mid
        else:
            hi = mid
    return lo


def min_max_gas_station_gap(stations, k, iterations=60):
    """Add k stations to minimise the largest gap between adjacent ones.

    ok(d): stations needed so every gap is <= d is sum(ceil(gap / d) - 1).
    Fewer needed as d grows, so ok is False ... True.
    """
    import math

    gaps = [b - a for a, b in zip(stations, stations[1:])]

    def ok(d):
        return sum(math.ceil(g / d) - 1 for g in gaps) <= k

    lo, hi = 0.0, max(gaps)
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


# ------------------------------------------------------------------------ tests


def test_isqrt_matches_math_isqrt():
    import math
    import random

    for n in range(0, 2000):
        assert isqrt(n) == math.isqrt(n)
    rng = random.Random(50)
    for _ in range(500):
        n = rng.randint(0, 10**30)
        assert isqrt(n) == math.isqrt(n)


def test_sqrt_and_cbrt_close_to_library():
    import math
    import random

    rng = random.Random(51)
    for _ in range(500):
        x = rng.uniform(0, 1e6) if rng.random() < 0.5 else rng.uniform(0, 1)
        assert math.isclose(sqrt_real(x), math.sqrt(x), rel_tol=1e-12, abs_tol=1e-12)
        y = rng.uniform(-1e6, 1e6) if rng.random() < 0.5 else rng.uniform(-1, 1)
        assert math.isclose(cbrt_real(y), math.copysign(abs(y) ** (1 / 3), y), rel_tol=1e-9, abs_tol=1e-12)


def test_max_average_matches_brute_force():
    import random

    rng = random.Random(52)
    for _ in range(300):
        nums = [rng.randint(-10, 10) for _ in range(rng.randint(1, 10))]
        k = rng.randint(1, len(nums))
        brute = max(
            sum(nums[i:j]) / (j - i)
            for i in range(len(nums))
            for j in range(i + k, len(nums) + 1)
        )
        assert abs(max_average_at_least_k(nums, k) - brute) < 1e-6
    assert abs(max_average_at_least_k([1, 12, -5, -6, 50, 3], 4) - 12.75) < 1e-6


def test_gas_station_matches_brute_force():
    import random

    def brute(stations, k):
        # Try every distribution of k new stations over the gaps (small inputs).
        gaps = [b - a for a, b in zip(stations, stations[1:])]
        best = float("inf")

        def go(i, left, worst):
            nonlocal best
            if i == len(gaps):
                best = min(best, worst)
                return
            for put in range(left + 1):
                go(i + 1, left - put, max(worst, gaps[i] / (put + 1)))

        go(0, k, 0.0)
        return best

    rng = random.Random(53)
    for _ in range(200):
        stations = sorted(rng.sample(range(0, 50), rng.randint(2, 5)))
        k = rng.randint(0, 5)
        assert abs(min_max_gas_station_gap(stations, k) - brute(stations, k)) < 1e-6


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
