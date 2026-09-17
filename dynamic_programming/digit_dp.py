"""Digit DP — count integers in [0, N] whose digits satisfy a property.

Signs: "how many numbers up to N (or in [L, R]) have ...": a digit sum limit,
       no repeated digits, no two adjacent equal digits, a given digit count.
       N is up to 10^18, so enumerating is out; the number of digits is not.
Approach: build the number digit by digit from the left. State:
            pos     — which digit we are placing
            tight   — the prefix so far equals N's prefix, so this digit is
                      capped at N[pos]; otherwise any 0-9 is allowed
            started — a non-zero digit has been placed (leading zeros are not
                      real digits: 007 has one digit, not three)
            extra   — whatever the property needs (sum so far, used-digit mask)
          Count for [L, R] as f(R) - f(L - 1).
Complexity: O(digits * states * 10).
Gotchas:
  - tight for the next digit is `tight and d == cap`, not just `d == cap`.
  - Forgetting `started` makes 0 look like a repeated digit in "00…07".
  - f(L - 1) with L = 0 asks about -1: return 0, don't call str(-1).
  - @cache on a nested function is per call — the digits are baked in, so
    the cache must not be shared across different N.

Run the tests at the bottom with:  python3 dynamic_programming/digit_dp.py
"""

import random
from functools import cache
from math import perm


# ---------------------------------------------------------------- implementation


def count_digit_sum_leq(N, S):
    """Count x in [0, N] with digit sum <= S."""
    if N < 0:
        return 0
    digits = list(map(int, str(N)))

    @cache
    def f(pos, tight, total):
        if total > S:
            return 0
        if pos == len(digits):
            return 1
        cap = digits[pos] if tight else 9
        return sum(f(pos + 1, tight and d == cap, total + d) for d in range(cap + 1))

    return f(0, True, 0)


def count_unique_digits(N):
    """Count x in [0, N] with no repeated digit (0 itself counts)."""
    if N < 0:
        return 0
    digits = list(map(int, str(N)))

    @cache
    def f(pos, tight, started, used):
        if pos == len(digits):
            return 1  # a completed number (all-leading-zeros is the number 0)
        cap = digits[pos] if tight else 9
        total = 0
        for d in range(cap + 1):
            if not started and d == 0:  # still a leading zero: uses nothing
                total += f(pos + 1, tight and d == cap, False, used)
            elif not used >> d & 1:
                total += f(pos + 1, tight and d == cap, True, used | 1 << d)
        return total

    return f(0, True, False, 0)


def count_in_range(count_upto, L, R, *args):
    """Numbers in [L, R] via two prefix counts."""
    return count_upto(R, *args) - count_upto(L - 1, *args)


# ------------------------------------------------------------------------ tests


def digit_sum(x):
    return sum(map(int, str(x)))


def unique(x):
    s = str(x)
    return len(set(s)) == len(s)


def test_digit_sum_matches_brute_force():
    random.seed(130)
    for _ in range(200):
        N, S = random.randint(0, 3000), random.randint(0, 30)
        assert count_digit_sum_leq(N, S) == sum(digit_sum(x) <= S for x in range(N + 1))


def test_unique_digits_matches_brute_force():
    brute = 0
    checkpoints = set(range(0, 1200)) | {9876, 10000, 98765}
    for x in range(98766):
        brute += unique(x)
        if x in checkpoints:
            assert count_unique_digits(x) == brute, x


def test_leading_zeros_trap():
    # Without `started`, 5 is read as "005" and rejected for its two zeros.
    def wrong(N):
        digits = list(map(int, str(N)))

        @cache
        def f(pos, tight, used):
            if pos == len(digits):
                return 1
            cap = digits[pos] if tight else 9
            return sum(
                f(pos + 1, tight and d == cap, used | 1 << d)
                for d in range(cap + 1) if not used >> d & 1
            )

        return f(0, True, 0)

    assert count_unique_digits(100) == 91  # 0..100 minus 11,22,...,99 and 100
    assert wrong(100) < 91


def test_ranges():
    assert count_in_range(count_digit_sum_leq, 0, 0, 0) == 1
    assert count_in_range(count_digit_sum_leq, 10, 20, 2) == 3  # 10, 11, 20
    random.seed(131)
    for _ in range(100):
        L = random.randint(0, 2000)
        R = random.randint(L, 2500)
        assert count_in_range(count_unique_digits, L, R) == sum(unique(x) for x in range(L, R + 1))


def test_huge_n():
    # Every 18-digit-or-fewer number below 10^18 has digit sum <= 162.
    assert count_digit_sum_leq(10**18 - 1, 162) == 10**18
    # 10-digit numbers with all digits distinct: 9 * 9!, plus all shorter ones.
    total = 1 + sum(9 * perm(9, k - 1) for k in range(1, 11))
    assert count_unique_digits(10**10) == total


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
