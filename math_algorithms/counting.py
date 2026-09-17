"""Counting principles — closed forms instead of enumeration.

Signs: "how many ways / arrangements / paths", n up to 10^9 so you cannot
       list them, "divisible by a or b", balanced parentheses, "prove a
       repeat must exist".
Approach: recognise the shape and reach for its formula.
  - Grid paths (m downs, n rights): choose which m of the m + n moves go down,
    C(m + n, m).
  - Stars and bars (n identical items into k bins): arrange n stars and
    k - 1 bars, C(n + k - 1, k - 1). With "each bin >= 1", pre-fill: n -> n - k.
  - Inclusion-exclusion: |A u B| = |A| + |B| - |A n B|. Multiples of a or b up
    to x is x//a + x//b - x//lcm(a, b); for more sets, alternate signs over
    subsets.
  - Catalan: C(2n, n) / (n + 1) — balanced parens, BST shapes, triangulations.
  - Pigeonhole: n + 1 items in n boxes forces a collision; it turns "does it
    exist" into "it always exists, now find it".
  - Monotone counts + binary search: "n-th number with property P" is the
    smallest x with count(x) >= n.
Complexity: O(1)-ish per formula, O(2^k) for k-set inclusion-exclusion,
            O(log(answer)) for count-then-search.
Gotchas:
  - Use lcm, not a * b, for the intersection of "divisible by a" and
    "divisible by b" (a = 4, b = 6: the overlap is multiples of 12, not 24).
  - Catalan division is exact only on the big-int value; mod a prime, multiply
    by the inverse of n + 1.
  - Stars and bars with zero bins: 1 way for 0 items, 0 ways otherwise.

Run the tests at the bottom with:  python3 math_algorithms/counting.py
"""

from binomial import comb_exact
from gcd_lcm import lcm


# ---------------------------------------------------------------- implementation


def grid_paths(m, n):
    """Monotone paths from (0, 0) to (m, n) moving only +row / +col."""
    return comb_exact(m + n, m)


def stars_and_bars(n, k, at_least_one=False):
    """Ways to put n identical items into k distinct bins."""
    if at_least_one:
        n -= k
    if n < 0:
        return 0
    if k == 0:
        return 1 if n == 0 else 0
    return comb_exact(n + k - 1, k - 1)


def catalan(n):
    return comb_exact(2 * n, n) // (n + 1)


def count_multiples(x, divisors):
    """How many of 1..x are divisible by at least one of `divisors`.

    Inclusion-exclusion over non-empty subsets: odd-sized subsets add, even
    ones subtract, each counting multiples of the subset's lcm.
    """
    k, total = len(divisors), 0
    for mask in range(1, 1 << k):
        l, bits = 1, 0
        for i in range(k):
            if mask >> i & 1:
                l = lcm(l, divisors[i])
                bits += 1
            if l > x:
                break
        if l <= x:
            total += x // l if bits & 1 else -(x // l)
    return total


def first_true(lo, hi, pred):
    """Smallest x in [lo, hi) with pred(x), for monotone pred; hi if none."""
    while lo < hi:
        mid = (lo + hi) // 2
        if pred(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def nth_magical(n, a, b):
    """n-th positive integer divisible by a or b (exact; LeetCode 878 wants % 1e9+7).

    count(x) is monotone, and the answer is at most n * min(a, b) because the
    multiples of min(a, b) alone already supply n candidates.
    """
    L = lcm(a, b)

    def count(x):
        return x // a + x // b - x // L

    return first_true(1, n * min(a, b) + 1, lambda x: count(x) >= n)


def subarray_sum_divisible_by_n(nums):
    """Pigeonhole: any n integers have a non-empty contiguous block whose sum
    is divisible by n. Returns (i, j) with sum(nums[i:j]) % n == 0.

    There are n + 1 prefix sums (including the empty one) but only n
    residues, so two of them collide; the block between them works.
    """
    n = len(nums)
    seen = {0: 0}
    s = 0
    for j, x in enumerate(nums, 1):
        s = (s + x) % n
        if s in seen:
            return seen[s], j
        seen[s] = j
    raise AssertionError("unreachable by pigeonhole")


# ------------------------------------------------------------------------ tests


def test_grid_paths_against_dp():
    for m in range(12):
        for n in range(12):
            dp = [[1] * (n + 1) for _ in range(m + 1)]
            for r in range(1, m + 1):
                for c in range(1, n + 1):
                    dp[r][c] = dp[r - 1][c] + dp[r][c - 1]
            assert grid_paths(m, n) == dp[m][n]
    assert grid_paths(0, 0) == 1
    assert grid_paths(2, 6) == 28  # LeetCode 62, m=3 n=7 grid


def test_stars_and_bars_against_enumeration():
    from itertools import product

    for k in range(0, 5):
        for n in range(0, 8):
            tuples = [t for t in product(range(n + 1), repeat=k) if sum(t) == n]
            assert stars_and_bars(n, k) == len(tuples), (n, k)
            positive = [t for t in tuples if all(v >= 1 for v in t)]
            assert stars_and_bars(n, k, at_least_one=True) == len(positive), (n, k)


def test_catalan_against_balanced_parentheses():
    from itertools import product

    def balanced(s):
        depth = 0
        for ch in s:
            depth += 1 if ch == "(" else -1
            if depth < 0:
                return False
        return depth == 0

    for n in range(0, 9):
        count = sum(balanced(s) for s in product("()", repeat=2 * n))
        assert catalan(n) == count
    assert [catalan(i) for i in range(10)] == [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862]


def test_catalan_recurrence_for_big_n():
    # C(0) = 1, C(n+1) = sum C(i) * C(n-i) — the "split at the root" recurrence
    c = [1]
    for n in range(80):
        c.append(sum(c[i] * c[n - i] for i in range(n + 1)))
    assert [catalan(i) for i in range(81)] == c


def test_count_multiples_against_brute_force():
    import random

    rng = random.Random(21)
    for _ in range(400):
        divs = [rng.randint(1, 30) for _ in range(rng.randint(1, 4))]
        x = rng.randint(0, 600)
        brute = sum(1 for v in range(1, x + 1) if any(v % d == 0 for d in divs))
        assert count_multiples(x, divs) == brute, (x, divs)


def test_intersection_uses_lcm_not_product():
    x, a, b = 100, 4, 6
    brute = sum(1 for v in range(1, x + 1) if v % a == 0 or v % b == 0)
    assert count_multiples(x, [a, b]) == brute == 33
    assert x // a + x // b - x // (a * b) != brute  # the classic mistake


def test_first_true():
    assert first_true(0, 10, lambda x: x >= 7) == 7
    assert first_true(0, 10, lambda x: True) == 0
    assert first_true(0, 10, lambda x: False) == 10
    assert first_true(5, 5, lambda x: True) == 5


def test_nth_magical_against_brute_force():
    import random

    rng = random.Random(22)
    for _ in range(300):
        a, b = rng.randint(1, 40), rng.randint(1, 40)
        n = rng.randint(1, 60)
        seq = [v for v in range(1, n * min(a, b) + 1) if v % a == 0 or v % b == 0]
        assert nth_magical(n, a, b) == seq[n - 1], (n, a, b)
    assert nth_magical(4, 2, 3) == 6
    assert nth_magical(10**9, 40000, 40000) == 4 * 10**13
    # too big to enumerate: check the defining properties instead
    n, a, b = 10**9, 39999, 40000
    x = nth_magical(n, a, b)
    assert x % a == 0 or x % b == 0
    assert count_multiples(x, [a, b]) == n
    assert count_multiples(x - 1, [a, b]) == n - 1


def test_pigeonhole_block():
    import random

    rng = random.Random(23)
    for _ in range(2000):
        nums = [rng.randint(-50, 50) for _ in range(rng.randint(1, 20))]
        i, j = subarray_sum_divisible_by_n(nums)
        assert 0 <= i < j <= len(nums)
        assert sum(nums[i:j]) % len(nums) == 0


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
